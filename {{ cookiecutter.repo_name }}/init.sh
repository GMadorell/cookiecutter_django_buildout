set -e

wget https://raw.githubusercontent.com/buildout/buildout/master/bootstrap/bootstrap.py

python bootstrap.py

./bin/buildout
