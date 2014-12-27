from __future__ import print_function
import os
import sys
import time

from encryptedfiles.encryptedfile import EncryptedFile
from encryptedfiles.encryptedjson import EncryptedJson

from fabric.decorators import task
from fabric.colors import red, green, blue, yellow
from fabric.api import env, run, local, sudo, put
from fabric.context_managers import cd

import subprocess

import boto
import boto.ec2
import boto.rds

from config import Config

from jinja2 import Template


####
## AMAZON EC2
####

aws_cfg = Config(open("aws.cfg"))

@task
def localhost():
    env.run = local
    env.hosts = ["localhost"]

@task
def target(instance_name, user="ec2-user"):
    """
    Sets the fab environment to the given instance_name.
    This instance_name has to be the tag "Name" of the ec2 instance
    we want to control.
    Used like: fab target:django1 *some_other_command*.
    """
    conn = connect_ec2()
    reservations = conn.get_all_instances()
    for res in reservations:
        for inst in res.instances:
            name = inst.tags["Name"]
            if name == instance_name:
                env.hosts = [inst.public_dns_name]
                env.key_filename = os.path.expanduser(os.path.join(
                    aws_cfg["key_dir"], "{}.pem".format(inst.key_name)))
    env.user = user
    env.run = run

def connect_ec2():
    return boto.ec2.connect_to_region(aws_cfg["region"],
            aws_access_key_id=aws_cfg["aws_access_key_id"],
            aws_secret_access_key=aws_cfg["aws_secret_access_key"])



## WEBAPP DEPLOYMENT

@task
def deploy_webapp_run(fresh=True):
    deploy_webapp(fresh)
    run_webapp_container()

@task
def deploy_webapp(fresh=True):
    handle_prerequisites(fresh)
    with cd("{{ cookiecutter.repo_name }}"):
        put("src/{{ cookiecutter.repo_name }}/config/keys/*", "src/{{ cookiecutter.repo_name }}/config/keys/")
        env.run("sudo docker build -t {{ cookiecutter.repo_name }}_appserver_deploy .")
    print(green("Succesfully deployed the {{ cookiecutter.repo_name }} appserver. "
                "Feel free to run 'fab run_webapp_container' ;)."))

def handle_prerequisites(fresh):
    if fresh:
        env.run("sudo yum install git")
        env.run("sudo yum install -y docker ; sudo service docker start")  # https://docs.docker.com/installation/amazon/
    env.run("rm -rf {{ cookiecutter.repo_name }}")
    env.run("git clone https://github.com/Skabed/{{ cookiecutter.repo_name }} {{ cookiecutter.repo_name }}")

@task
def run_webapp_container():
    docker_ps = env.run("sudo docker ps -a")
    if "{{ cookiecutter.repo_name }}_appserver_running" in docker_ps:
        env.run("sudo docker rm -f {{ cookiecutter.repo_name }}_appserver_running")
    env.run("sudo docker run --name {{ cookiecutter.repo_name }}_appserver_running -p 80:80 {{ cookiecutter.repo_name }}_appserver_deploy")

@task
def stop_webapp_container():
    env.run("sudo docker stop {{ cookiecutter.repo_name }}_appserver_running")



## DATABASE DEPLOYMENT

@task
def deploy_db_run(fresh=True):
    deploy_db(fresh)
    run_db_container()

@task
def deploy_db(fresh=True):
    handle_prerequisites(fresh)
    with cd("{{ cookiecutter.repo_name }}"):
        put("src/{{ cookiecutter.repo_name }}/config/keys/*", "src/{{ cookiecutter.repo_name }}/config/keys/")
        env.run("bash init.sh")
        env.run("bin/fab build_db_dockerfile")
    print(green("Succesfully deployed the {{ cookiecutter.repo_name }} database. "
                "Feel free to run 'fab run_db_container' ;)."))

@task
def build_db_dockerfile():
    dockerfile_template = Template(open(".server_config/db/psql_dockerfile.template").read())
    db_settings = get_enc_json("prod_db.json")
    try:
        with open(".server_config/db/psql_dockerfile", "w") as psql_dockerfile:
            psql_dockerfile.write(dockerfile_template.render(
                db_user = db_settings["database"]["USER"],
                db_password = db_settings["database"]["PASSWORD"],
                db_name = db_settings["database"]["NAME"]))
        env.run("sudo docker build -t {{ cookiecutter.repo_name }}_db_deploy - < .server_config/db/psql_dockerfile")
    finally:
        os.remove(".server_config/db/psql_dockerfile")

@task
def run_db_container():
    docker_ps = env.run("sudo docker ps -a")
    if "{{ cookiecutter.repo_name }}_db_running" in docker_ps:
        env.run("sudo docker rm -f {{ cookiecutter.repo_name }}_db_running")
    env.run("sudo docker run --name {{ cookiecutter.repo_name }}_db_running -p 80:80 {{ cookiecutter.repo_name }}_db_deploy")

@task
def stop_db_container():
    env.run("sudo docker stop {{ cookiecutter.repo_name }}_db_running")



####
## AMAZON RDS
####

@task
def create_rds_instance(database_id,
    allocated_storage=5, 
    instance_class="db.t2.micro"):
    db_settings = get_enc_json("prod_db.json")
    conn = connect_rds()
    db = conn.create_dbinstance(
        id=database_id,
        allocated_storage=allocated_storage,
        instance_class=instance_class,
        master_username=db_settings["database"]["USER"],
        master_password=db_settings["database"]["PASSWORD"],
        db_name=db_settings["database"]["NAME"],
        engine="postgres",
        port=5432,
    )

    print("Waiting for db to be available:", end="")
    time_waited = 0
    while db.status.lower().strip() != "available":
        time.sleep(1)
        time_waited += 1
        print(".", end="")
        if time_waited % 30 == 0:
            print("\nDB status: {} (waited for {} seconds)."\
                  .format(db.status.lower(), time_waited), end="") 
        sys.stdout.flush()
        db.update()

    print(green("\nSuccessfully created db instance."))
    print(green("DB Endpoint: {}".format(db.endpoint)))
    print(yellow("Remember to manually set the security group."))

def connect_rds():
    conn = boto.rds.connect_to_region(
            aws_cfg["region"],
            aws_access_key_id=aws_cfg["aws_access_key_id"],
            aws_secret_access_key=aws_cfg["aws_secret_access_key"])
    return conn


####
## Utils
####

BASE_CONFIG = os.path.join("src", "{{ cookiecutter.repo_name }}", "config")
CONFIG_DIRNAME = os.path.join(BASE_CONFIG, "plain")
ENCRYPTED_DIRNAME = os.path.join(BASE_CONFIG, "encrypted")
KEYS_DIR = os.path.join(BASE_CONFIG, "keys")

def get_enc_file(filename):
    return EncryptedFile(os.path.join(ENCRYPTED_DIRNAME, filename), get_key())

def get_enc_json(filename):
    return EncryptedJson(os.path.join(ENCRYPTED_DIRNAME, filename), get_key())

@task
def encrypt_config():
    cfg_filenames = [f for f in os.listdir(CONFIG_DIRNAME)
                     if os.path.isfile(os.path.join(CONFIG_DIRNAME, f))]

    for filename in cfg_filenames:
        if ".gitignore" in filename:
            continue
        with open(os.path.join(CONFIG_DIRNAME, filename), "r") as cfg_file:
            enc_file = EncryptedFile(os.path.join(ENCRYPTED_DIRNAME, filename),
                                     get_key())
            enc_file.write(cfg_file.read())


def get_key():
    with open(os.path.join(KEYS_DIR, "cfg_key.key"), "r") as cfg_key_file:
        return cfg_key_file.read()
