import time

from pprint import pprint
from configparser import ConfigParser
from trading_factory.factory import TradingFactory
# from azure.mgmt.datafactory.models import *
from azure.mgmt.datafactory.models import Factory
from azure.mgmt.datafactory.models import LinkedService
from azure.mgmt.datafactory.models import LinkedServiceReference
from azure.mgmt.datafactory.models import AzureFunctionLinkedService
from azure.mgmt.datafactory.models import AzureKeyVaultLinkedService
from azure.mgmt.datafactory.models import FactoryGitHubConfiguration
from azure.mgmt.datafactory.models import AzureKeyVaultSecretReference

# Initialize the Parser.
config = ConfigParser()

# Read the file.
config.read('config/config.ini')

# Get the specified credentials.
subscription_id = config.get('main', 'subscription_id')

# Create a Factory Client.
factory_client = TradingFactory(subscription_id=subscription_id)


def create_new_factory():

    # Define the GitHub Repo Configuration.
    repo_config = FactoryGitHubConfiguration(
        account_name='areed1192',
        collaboration_branch='master',
        repository_name='trading-data-factory',
        root_folder='/data-factory/',
        type='FactoryGitHubConfiguration'
    )

    # Create a new Data Factory Client.
    trade_factory_new = factory_client.factory_mgmt_client.factories.create_or_update(
        resource_group_name='sigma-coding-tutorials',
        factory_name='TradingFactory',
        factory=Factory(
            location='eastus',
            repo_configuration=repo_config
        )
    )

    # Wait till it was successful.
    while trade_factory_new.provisioning_state != 'Succeeded':

        # Grab the new client.
        df = factory_client.factory_mgmt_client.factories.get(
            'sigma-coding-tutorials',
            'TradingFactory'
        )

        time.sleep(1)


create_factory_test = False
if create_factory_test:
    create_new_factory()

# Grab the Linked Services.
linked_services = list(
    factory_client.factory_mgmt_client.linked_services.list_by_factory(
        resource_group_name='sigma-coding-tutorials',
        factory_name='SigmaDataFactory'
    )
)

# Loop through the Linked Service.
for linked_service in linked_services:

    # Reassignment to fix intellisense bug.
    linked_service: LinkedService = linked_service

    # Print out.
    pprint(linked_service.as_dict())


create_link_service = True

if create_link_service:

    # In this part we will demonstrate how to create different linked services.
    # Now, a lot of the services we leverage on Azure require some form of authentication.
    # Because of this we will need to provide the credentials for them in order
    # to use them in our data factory.
    #
    # To grab those credentials, we will create a linked service to our Azure Key Vault.
    # Then we will grab a secret from our Azure Vault, the secret will represent a
    # connection string to a SQL Database. The database is where we will store our data
    # from the TD Ameritrade API.
    #
    # Here are the steps in this section:
    #   1. Create a Linked Service for an Azure Key Vault Service.
    #   2. Create a AzureKeyVaultSecretReference to the secret we want to pull from the
    #      the key vault. Remember it's the connection string.
    #   3. Create a linked service for a SQL database.
    #   4. Connect to the SQL Database.
    # SqlDatabaseConnection

    # Create a new AzureKeyVaultLinkedService.
    azure_key_vault_trading = factory_client.factory_mgmt_client.linked_services.create_or_update(
        resource_group_name='sigma-coding-tutorials',
        factory_name='SigmaDataFactory',
        linked_service_name='AzureKeyVaultTrading',
        properties=AzureKeyVaultLinkedService(
            base_url="https://sigma-key-vault.vault.azure.net/"
        )
    )
    pprint(azure_key_vault_trading.as_dict())

    # Create Linked Refernce to the Azure key Vault.
    azure_key_vault_trading_ls = LinkedServiceReference(
        reference_name='AzureKeyVaultTrading'
    )

    # Grab the Secret from the Key Vault.
    azure_key_vault_secret_trading_ls = AzureKeyVaultSecretReference(
        store=azure_key_vault_trading_ls,
        secret_name="sigma-azure-news-function-key"
    )
    print(azure_key_vault_secret_trading_ls)

    # Create a new Azure Function Service. This will act as a "template."
    function_string_app = AzureFunctionLinkedService(
        store=azure_key_vault_trading_ls,
        secret_name="sigma-azure-news-function-key",
        function_app_url="https://sigma-function-news.azurewebsites.net",
        function_key=azure_key_vault_secret_trading_ls
    )
    print(function_string_app)

    # Take the template and actually create the new service. If you went 
    # in the UI you should see it after this.
    create_azure_news_func = False
    if create_azure_news_func:

        azure_news_func = factory_client.factory_mgmt_client.linked_services.create_or_update(
            resource_group_name='sigma-coding-tutorials',
            factory_name='SigmaDataFactory',
            linked_service_name='AzureKeyVaultTradingFunction',
            properties=function_string_app

        )
        pprint(azure_news_func.as_dict())






# {
#     "name": "AzureNewsArticlePull",
#     "properties": {
#         "annotations": [],
#         "type": "AzureFunction",
#         "typeProperties": {
#             "functionAppUrl": "https://sigma-function-news.azurewebsites.net",
#             "functionKey": {
#                 "type": "AzureKeyVaultSecret",
#                 "store": {
#                     "referenceName": "SigmaKeyVault",
#                     "type": "LinkedServiceReference"
#                 },
#                 "secretName": "sigma-azure-news-function-key"
#             }
#         }
#     }
# }

# # List all the data factories for our account.
# for factory in factory_client.factory_mgmt_client.factories.list():

#     # Do reassignment to help fix intellisense error.
#     factory: Factory = factory

#     # Print it out as a dictionary.
#     pprint(factory.as_dict())
#     pprint(factory.is_xml_model())
#     pprint(factory.additional_properties)
#     pprint(factory.validate())
