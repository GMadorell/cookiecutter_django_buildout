#!/bin/bash

set -e

# Generate a random key to encrypt the config files.
bash gen_key.sh
rm gen_key.sh

bash init.sh

# .gitignore_template -> .gitignore, recursively.
find . -iname ".gitignore_template" -exec rename "s/.gitignore_template/.gitignore/" '{}' \;

bin/fab encrypt_config

bin/compass create src/assets -r bootstrap-sass --using bootstrap

git init
git add .
git commit -m "First commit"