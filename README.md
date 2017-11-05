# Introduction 
High scale parallel processing architecture in Azure based on Redis RQ and written in Azure.

# Dev Setup

### Pyenv for multiple python versions (macOS)
brew install pyenv
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bash_profile
exec "$SHELL"
xcode-select --install
CFLAGS="-I$(brew --prefix openssl)/include" \
LDFLAGS="-L$(brew --prefix openssl)/lib" \
pyenv install -v 2.7.5
pyenv rehash
cd <yourlocalpath>/azure-python-redis-queue-processor
pyenv local 2.7.5
python --version

### Dependencies
- [Python 2.7.5](http://#)
- [PIP Package Manager](https://pip.pypa.io/en/stable/installing/)
- [Python code editor](http://#)
- [Git](http://#)
- [Azure CLI](http://)

### Setup Instructions
1. Git clone repo
2. Install dependencies
3. Open bash shell
4. Install Azure SDKs
```
sudo pip install --ignore-installed azure-keyvault
sudo pip install --ignore-installed msrestazure
sudo pip install --ignore-installed adal
sudo pip install --ignore-installed azure-storage
sudo pip install --ignore-installed enum
sudo pip install --ignore-installed redis
```