import pickle
from enum import Enum
from azure.storage.queue import QueueService, models
from config import Config
from azurerest import AzureRest

class AzureResource(Enum):
    vm = 'vm',
    vm_scale_set = 'vm_scale_set'

class MetricsLogger(object):
    """
    Logs Microsoft Azure resource metrics to storage
    """

    def __init__(self, logger):
        """
        Constructor. Initializes storage, config and other dependencies

        :param logger logger: The logger instance to use for logging
        """
        self.logger = logger
        self.config = Config()
        self.azure_rest = AzureRest(logger)
        if(self.init_storage_service() is False):
            raise Exception("Errors occured instantiating metrics storage service.")

        if(self.init_storage() is False):
            raise Exception("Errors occured validating metrics table exists.")

    def init_storage_service(self):
        """
        Initializes the storage service client using values from config.py.

        :return: True on succeess. False on failure.
        :rtype: boolean
        """
        try:
            # creates instance of QueueService to use for completed metrics storage
            self.storage_service_queue = QueueService(account_name = self.config.metrics_storage, sas_token = self.config.metrics_sas_token)
            
            # set the encode function for objects stored as queue message to noencode, serialization will be handled as a string by pickle
            # http://azure-storage.readthedocs.io/en/latest/ref/azure.storage.queue.queueservice.html
            # http://azure-storage.readthedocs.io/en/latest/_modules/azure/storage/queue/models.html
            self.storage_service_queue.encode_function = models.QueueMessageFormat.noencode
            
            return True
        except Exception as ex:
            self._log_exception(ex, self.init_storage_service.__name__)
            return False

    def init_storage(self):
        """
        Initializes storage queue, creating it if it doesn't exist.

        :return: True on succeess. False on failure.
        :rtype: boolean
        """
        try:
            # will create metrics storage queue if it doesn't exist
            self.storage_service_queue.create_queue(self.config.metrics_storage)
            return True
        except Exception as ex:
            self._log_exception(ex, self.init_storage.__name__)
            return False

    def _log_exception(self, exception, functionName):
        """
        Logs an exception to the logger instance for this class.

        :param Exeption exception: The exception thrown.
        :param str functionName: Name of the function where the exception occurred.
        """
        self.logger.debug("Exception occurred in: " + functionName)
        self.logger.debug(type(exception))
        self.logger.debug(exception)
    
    def resource_provider_lookup(self, azureResource):
        """
        Returns Azure Resource Provider string from enum.

        :param Enum azureResource: The AzureResource to retrieve the Resource Provider for.
        :return: Azure Resource Provider string
        :rtype: str
        """
        switch = {
            AzureResource.vm: "Microsoft.Compute",
            AzureResource.vm_scale_set: "Microsoft.Compute",
        }
        return switch.get(azureResource, None)
    
    def resource_type_lookup(self, azureResource):
        """
        Returns Azure Resource Type string from enum.

        :param Enum azureResource: The AzureResource to retrieve the Resource Type for.
        :return: Azure Resource Type string
        :rtype: str
        """
        switch = {
            AzureResource.vm: "virtualMachines",
            AzureResource.vm_scale_set: "virtualMachineScaleSets",
        }
        return switch.get(azureResource, None)

    def get_vms_in_resource_group(self, resourceGroup):
        """
        Calls Azure to get a list of VMs in a resource group

        :param str resourceGroup: The Azure Resource Group containing the VMs to list
        :return: Array of vm names
        :rtype: Array[str]
        """
        vmListArray = []

        try:
            # get the resource provider and resource type we need for the URI
            resourceProvider = self.resource_provider_lookup(AzureResource.vm)
            resourceType = self.resource_type_lookup(AzureResource.vm)

            # build the full Microsoft Azure REST uri
            baseUri = self.buildAzureMetricsBaseUri(resourceGroup, resourceProvider, resourceType, None)
            uri = baseUri + "?api-version=2017-03-30"
            #https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.Compute/virtualmachines?api-version={apiVersion}

            # execute the HTTP GET request and capture the response
            vmList = self.azure_rest.http_get(uri)

            if(vmList is not None):
                # iterate through the list of vms and build a string array of vm names
                for item in vmList.viewitems():
                    value = item[0], item[1]
                    vmName = value[1][0]['name']
                    #vmName is unicode encoded, so we need to get the string
                    if(vmName is not None):
                        vmListArray.append(vmName.encode("utf-8"))

        except Exception as ex:
            self._log_exception(ex, self.get_vms_in_resource_group.__name__)
            return False

        return vmListArray

    def buildAzureMetricsBaseUri(self, resourceGroup, resourceProvider, resourceType, resourceName):
        """
        Builds a base Azure Metrics API URI

        :param str resourceGroup: The Azure Resource Group to use in the URI
        :param str resourceProvider: The Azure Resource Provider to use in the URI
        :param str resourceType: The Azure Resource Type to use in the URI
        :param str resourceName: The Azure Resource name to use in the URI
        :return: Base Azure Metrics API URI
        :rtype: str
        """
        # build the base Microsoft Azure REST uri
        baseUri = ''.join(['https://management.azure.com',
                    '/subscriptions/', self.config.subscription_id,
                    '/resourceGroups/', resourceGroup,
                    '/providers/', resourceProvider,
                    '/', resourceType])
        
        # add a specific resource name to the URI if we received one
        if(resourceName is not None):
            baseUri = baseUri + '/' + resourceName

        return baseUri

    def get_metrics(self, azureResource, resourceGroup, resourceName):
        """
        Get metrics using the Microsoft Insights Azure metrics service for a resource

        :param Enum azureResource: The Azure Resource to retrieve metrics for
        :param str resourceGroup: The Azure Resource Group to retrieve metrics for
        :param str resourceName: The Azure Resource name to retrieve metrics for
        :return: Azure Metrics response
        :rtype: Object
        """
        resourceProvider = self.resource_provider_lookup(azureResource)
        resourceType = self.resource_type_lookup(azureResource)
        baseUri = self.buildAzureMetricsBaseUri(resourceGroup, resourceProvider, resourceType, resourceName)
        uri = baseUri + '/providers/microsoft.insights/metrics?api-version=2017-05-01-preview'
        return self.azure_rest.http_get(uri)

    def capture_vm_metrics(self):
        """
        Iterates through all processing VMs and captures current VM metrics to storage.
        """
        # get all VMs in the resource group specififed in the config
        vmList = self.get_vms_in_resource_group(self.config.vm_resource_group)
        
        # iterate through each vm in the list
        for vmname in vmList:
            try:
                # get the metrics from the Azure Metrics service for this vm
                vmmetrics = self.get_metrics(AzureResource.vm, self.config.vm_resource_group, vmname)

                # write the metrics out to the storage queue
                vmmetricsSerialized = pickle.dumps(vmmetrics)
                self.storage_service_queue.put_message(self.config.metrics_storage, vmmetricsSerialized)

            except Exception as ex:
                self._log_exception(ex, self.capture_vm_metrics.__name__)