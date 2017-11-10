yum install -y wget
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py

pip install azure-storage
pip install azure-keyvault
pip install cryptography
pip install rq

tar -xzf processorscripts.tar.gz

python processorconfiguration.py
python processor.py data/aes.encrypted --redisHost $1 --redisPort 6379 2>&1 | python queuelogger.py