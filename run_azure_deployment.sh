# Script that will deploy to specified resource group and monitor for completion
# ex: sh run_azure_deployment.sh <ResourceGroup>
export PYTHONPATH=.

#Clean Environment
python samples/clearResultsAndQueues.py

START_TIME=$SECONDS

# Deploy Workload
az group deployment create --template-file arm/azuredeploy.json --parameters arm/azuredeploy.parameters.json -g $1 

ELAPSED_TIME=$(($SECONDS - $START_TIME))
echo "Azure deployment completed in: $(($ELAPSED_TIME/60)) min $(($ELAPSED_TIME%60)) sec"  

# Monitor Workload Status
python -u samples/getWorkloadStatus.py

  