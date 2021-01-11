
from typing import List
from typing import Dict
from typing import Union

from trading_factory.cred_wrapper import CredentialWrapper
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.mgmt.datafactory import DataFactoryManagementClient


class TradingFactory():

    def __init__(self, subscription_id: str):
        
        self.subscription_id = subscription_id

        self._default_credentials: DefaultAzureCredential =  DefaultAzureCredential()

        # azure-mgmt-datafactory has not been updated to use azure.core, 
        # so we need to use the Credential Wrapper.
        self._default_credentials = CredentialWrapper()
    
    @property
    def factory_mgmt_client(self) -> DataFactoryManagementClient:
        
        return DataFactoryManagementClient(
            self._default_credentials,
            self.subscription_id
        )


    # def auth(self) -> object:

    #     # Define the URL to our Blob Client Service.
    #     account_url = 'https://sigmafunctionnews.blob.core.windows.net/'

    #     # Create a Secret Client.
    #     secret_client = SecretClient(
    #         vault_url='https://sigma-key-vault.vault.azure.net/',
    #         credential=default_credential
    #     )