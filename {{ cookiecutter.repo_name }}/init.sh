set -e

wget https://raw.githubusercontent.com/buildout/buildout/master/bootstrap/bootstrap.py -O bootstrap.py

python bootstrap.py

./bin/buildout
