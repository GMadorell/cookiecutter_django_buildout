"""
Django settings for djagolb project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from encryptedfiles.encryptedjson import EncryptedFile

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_PROJECT = os.path.dirname(__file__)

BASE_CONFIG = os.path.join(os.path.dirname(__file__), "config")
CONFIG_DIRNAME = os.path.join(BASE_CONFIG, "plain")
ENCRYPTED_DIRNAME = os.path.join(BASE_CONFIG, "encrypted")
KEYS_DIR = os.path.join(BASE_CONFIG, "keys")

enc_path = lambda enc_filename: os.path.join(ENCRYPTED_DIRNAME, enc_filename)
get_key = lambda: open(os.path.join(KEYS_DIR, "cfg_key.key")).read()

def setup_encrypted_settings(settings_name):
    print("Trying to import {} settings.".format(settings_name))
    settings_py_name = "{}.py".format(settings_name)
    settings_tmp_path = os.path.join(BASE_PROJECT, settings_py_name)
    with open(settings_tmp_path, "w") as settings_tmp:
        settings_enc_file = EncryptedFile(enc_path(settings_py_name), get_key())
        settings_tmp_content = settings_enc_file.read()
        settings_tmp.write(settings_tmp_content)
    return settings_tmp_path

tmp_path = setup_encrypted_settings("common")
try:
    from .common import *
finally:
    os.remove(tmp_path)

if os.environ.get("DJANGO_PRODUCTION", False):
    tmp_path = setup_encrypted_settings("production")
    try:
        from .production import *
    finally:
        os.remove(tmp_path)
else:
    tmp_path = setup_encrypted_settings("development")
    try:
        from .development import *
    finally:
        os.remove(tmp_path)



