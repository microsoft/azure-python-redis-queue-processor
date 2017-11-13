yum install -y wget
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py

pip install azure-storage
pip install azure-keyvault
pip install cryptography
pip install rq

tar -xzf app.tar.gz

python app/processorconfiguration.py
python app/processor.py data/aes.encrypted --redisHost $1 --redisPort 6379 2>&1 | python app/queuelogger.py