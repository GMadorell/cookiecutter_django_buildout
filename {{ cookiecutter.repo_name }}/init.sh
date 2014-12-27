set -e

virtualenv --no-site-packages venv

wget http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py -O bootstrap.py

venv/bin/pip install --upgrade setuptools
venv/bin/python bootstrap.py

./bin/buildout