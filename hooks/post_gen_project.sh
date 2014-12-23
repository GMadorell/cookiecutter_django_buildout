#!/bin/bash

set -e

# Generate a random key to encrypt the config files.
bash gen_key.sh
rm gen_key.sh

bash init.sh

git init
git add .
git commit -m "First commit"