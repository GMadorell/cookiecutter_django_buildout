

from ubuntu:14.04

run apt-get update -y
run apt-get upgrade -y

run apt-get install -y python \
                       python-dev \
                       python-setuptools \
                       python-software-properties \
                       wget \
                       pandoc \
                       git \
                       vim \
                       
                       sqlite3 \
                       nginx \
                       supervisor


add . /webapps/{{ cookiecutter.repo_name }}/

run cd /webapps/{{ cookiecutter.repo_name }}/ && \
    	bash init.sh && \
    	bin/django syncdb --noinput && \
    	ln -s /webapps/{{ cookiecutter.repo_name }}/.server_config/{{ cookiecutter.repo_name }}_nginx.conf /etc/nginx/sites-enabled/ && \
    	ln -s /webapps/{{ cookiecutter.repo_name }}/.server_config/{{ cookiecutter.repo_name }}_supervisor.conf /etc/supervisor/conf.d/


run rm /etc/nginx/sites-enabled/default
run sudo service nginx restart

expose 80
workdir /webapps/{{ cookiecutter.repo_name }}/
cmd bin/python .server_config/entry_point.py