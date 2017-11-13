export PYTHONPATH=.
python samples/CopyScriptsForArmTemplate.py

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
