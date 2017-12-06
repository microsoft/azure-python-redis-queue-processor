yum install -y wget
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py

pip install azure-storage
pip install azure-keyvault
pip install cryptography
pip install rq
pip install adal
pip install requests
pip install futures

tar -xzf app.tar.gz

python app/schedulerconfiguration.py $1
python app/scheduler-unencrypted.py data/data.encrypted --redisHost $2 --redisPort 6379 2>&1 | python app/queuelogger.py
