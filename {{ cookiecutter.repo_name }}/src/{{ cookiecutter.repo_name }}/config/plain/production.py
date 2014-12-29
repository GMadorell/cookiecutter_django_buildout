import os
from encryptedfiles.encryptedjson import EncryptedJson


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

BASE_CONFIG = os.path.join(os.path.dirname(__file__), "config")
CONFIG_DIRNAME = os.path.join(BASE_CONFIG, "plain")
ENCRYPTED_DIRNAME = os.path.join(BASE_CONFIG, "encrypted")
KEYS_DIR = os.path.join(BASE_CONFIG, "keys")

enc_path = lambda enc_filename: os.path.join(ENCRYPTED_DIRNAME, enc_filename)
get_key = lambda: open(os.path.join(KEYS_DIR, "cfg_key.key")).read()

prod_db_settings = EncryptedJson(enc_path("prod_db.json"), get_key())

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    "default": prod_db_settings["database"]
}