import os
from encryptedfiles.encryptedfile import EncryptedFile

from fabric.decorators import task


BASE_CONFIG = "src/{{ cookiecutter.repo_name }}/config"
CONFIG_DIRNAME = os.path.join(BASE_CONFIG, "plain")
ENCRYPTED_DIRNAME = os.path.join(BASE_CONFIG, "encrypted")
KEYS_DIR = os.path.join(BASE_CONFIG, "keys")


@task
def encrypt_config():
    cfg_filenames = [f for f in os.listdir(CONFIG_DIRNAME)
                     if os.path.isfile(os.path.join(CONFIG_DIRNAME, f))]

    for filename in cfg_filenames:
        with open(os.path.join(CONFIG_DIRNAME, filename), "r") as cfg_file:
            enc_file = EncryptedFile(os.path.join(ENCRYPTED_DIRNAME, filename),
                                     get_key())
            enc_file.write(cfg_file.read())


def get_key():
    with open(os.path.join(KEYS_DIR, "cfg_key.key"), "r") as cfg_key_file:
        return cfg_key_file.read()