import subprocess
import os

SERVER_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
GUNICORN_CFG_PATH = os.path.join(SERVER_CONFIG_DIR, "gunicorn")
BASE_DIR = os.path.dirname(SERVER_CONFIG_DIR)

def start():
    # Stop gunicorn if it's running
    if os.path.isfile(os.path.join(GUNICORN_CFG_PATH, "instance.pid")):
        gunicornctl_command = "{}/bin/gunicornctl stop".format(BASE_DIR) 
        subprocess.call(gunicornctl_command, shell=True)
    remove_if_exists(os.path.join(GUNICORN_CFG_PATH, "gunicorn.sock"))

    if not is_nginx_running():
        print("Trying to restart Nginx before continuing.")
        subprocess.call("sudo service nginx restart", shell=True)

    subprocess.call("supervisord -n", shell=True)

def is_nginx_running():
    try:
        status = subprocess.check_output("sudo service nginx status",
                                         stderr=subprocess.STDOUT,
                                         shell=True)
    except subprocess.CalledProcessError as error:
        status = error.output

    if "is running" in status.lower():
        print("Nginx seems to be running.")
        return True
    else:
        print("Nginx seems to not be running"
              "(got status: {}).".format(status.strip("\n")))
        return False

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)


if __name__ == "__main__":
    start()
