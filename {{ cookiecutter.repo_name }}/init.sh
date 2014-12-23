set -e

virtualenv --no-site-packages venv

wget https://raw.githubusercontent.com/buildout/buildout/master/bootstrap/bootstrap.py -O bootstrap.py

venv/bin/python bootstrap.py

./bin/buildout