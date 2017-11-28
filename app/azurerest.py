"""
Azurerest.py creates HTTP requests with Azure user agent and access token headers to enable easy communication with Azure APIs.

module deps:
pip install adal
pip install requests
"""
import platform
import requests
import adal
from config import Config

class AzureRest(object):
    """
    Provides Azure REST API request functionality, adding all necessary headers and access tokens
    """

    def __init__(self, logger):
        """
        Constructor
        """
        self.config = Config()
        self.logger = logger
    
    def _log_exception(self, exception, functionName):
        """
        Logs an exception to the logger instance for this class.

        :param Exeption exception: The exception thrown.
        :param str functionName: Name of the function where the exception occurred.
        """
        self.logger.debug("Exception occurred in: " + functionName)
        self.logger.debug(type(exception))
        self.logger.debug(exception)

    def get_user_agent(self):
        """
        Returns a user agent string for use in Azure REST API requests
        :return: User agent string
        :rtype: str
        """
        user_agent = "python/{} ({}) requests/{} app/AzureMetrics".format(
            platform.python_version(),
            platform.platform(),
            requests.__version__)
        return user_agent

    def get_access_token(self):
        """
        Returns an access token for use in Azure REST API requests
        :return: Access token or None on failure
        :rtype: str
        """
        try:
            context = adal.AuthenticationContext('https://login.microsoftonline.com/' + self.config.tenant_id)
            token_response = context.acquire_token_with_client_credentials('https://management.core.windows.net/', self.config.service_principal_client_id, self.config.service_principal_secret)
            
            return token_response.get('accessToken')

        except Exception as ex:
            self._log_exception(ex, self.get_access_token.__name__)
            return None

    def http_get(self, uri):
        """
        Executes Azure REST API HTTP GET request
        :param str uri: The uri to use.
        :return: Response or None on failure
        :rtype: object
        """
        try:
            accessToken = self.get_access_token()
            headers = {"Authorization": 'Bearer ' + accessToken}
            headers['User-Agent'] = self.get_user_agent()
            return requests.get(uri, headers=headers).json()
        except Exception as ex:
                self._log_exception(ex, self.http_get.__name__)
                return None