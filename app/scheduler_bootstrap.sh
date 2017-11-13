yum install -y wget
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py

pip install azure-storage
pip install azure-keyvault
pip install cryptography
pip install rq

WORKDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

tar -xzf app.tar.gz -C $WORKDIR

touch $HOME/crontab
($HOME/crontab -l | echo "* * * * * python $WORKDIR/validator.py --redisHost $1 --redisPort 6379 >/dev/null 2>&1") | $HOME/crontab -
sudo /bin/systemctl start crond.service

python app/schedulerconfiguration.py
mv scheduler-unencrypted.py app/scheduler-unencrypted.py 
python app/scheduler-unencrypted.py data/data.encrypted --redisHost $1 --redisPort 6379 2>&1 | python app/queuelogger.py
