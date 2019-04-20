import os
from utils import exec_sync

def run_remote_command(ip, capture_out=True):
    output = exec_sync('ssh {} -o StrictHostKeyChecking=no "{}"'.format(ip),
                       capture_out=capture_out, shell=True)
    return output

def get_local_user():
    current_user = exec_sync(["whoami"], "", "", "")
    return current_user.strip()

def upload_file(local_path, ip, dest_path):
    exec_sync("scp {} {}@{}:{}".format(local_path, get_local_user(), ip, dest_path),
              capture_out=False, shell=True)

#def upload_script(script, ip):
#    upload_fil(e
