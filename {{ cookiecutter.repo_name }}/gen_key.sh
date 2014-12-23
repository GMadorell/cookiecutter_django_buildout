#!/bin/bash

set -e

# Generate a random key to encrypt the config files.
random_key=$(openssl rand -base64 512)
echo "$random_key" >> src/{{ cookiecutter.repo_name }}/config/keys/cfg_key.key