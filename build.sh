export PYTHONPATH=.

echo "This will create new AES key (if necessary), generate data, and upload it to Azure"
echo "Do you want to continue? [y/n]"
read data
if [[ $data = y ]]
then
    # Generate & upload encryption key and encrypt data
    python samples/buildKeyAndData.py
fi

echo "This will create a new app package and upload it to Azure and setup the local Docker Environment"
echo "Do you want to continue? [y/n]"
read upload
if [[ $upload = y ]]
then
    # Upload scripts
    python samples/buildScripts.py

    # Cleanup docker-env
    rm -rf docker-env
    mkdir -p docker-env

    # copy main tar file
    mv app.tar.gz docker-env/app.tar.gz

    # Copy bootstrap scripts
    cp app/processor_bootstrap.sh docker-env/processor_bootstrap.sh
    cp app/scheduler_bootstrap.sh docker-env/scheduler_bootstrap.sh

    # Copy encoded config file to CustomData file
    mkdir -p docker-env/waagent
    cp config/config.json.encoded docker-env/waagent/CustomData
    read -p "Press any key to exit..."
fi