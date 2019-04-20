import os
from utils import exec_sync

REMOTE_SCRIPT_ROOT = "/tmp/outsource/scripts/"

def run_remote_command(ip, command, capture_out=True):
    print("run remote command")
    output = exec_sync('ssh {} -o StrictHostKeyChecking=no "{}"'.format(ip, command),
                       capture_out=capture_out, shell=True)
    return output

def get_local_user():
    print("get local user")
    current_user = exec_sync(["whoami"], "", "", "")
    return current_user.strip()

def upload_file(local_path, ip, dest_path):
    print("upload file")
    dirname = os.path.dirname(dest_path)
    run_remote_command(ip, "mkdir -p {}".format(dirname))
    exec_sync("scp {} {}@{}:{}".format(local_path, get_local_user(), ip, dest_path),
              capture_out=False, shell=True)

def upload_script(script_path, ip):
    print("upload script")
    basename = os.path.basename(script_path)
    upload_file(script_path, ip, "{}{}".format(REMOTE_SCRIPT_ROOT, basename))

def run_remote_script(script_path, ip, capture_out=True):
    print("run remote command")
    upload_script(script_path, ip)
    basename = os.path.basename(script_path)
    return run_remote_command(ip, "bash {}{}".format(REMOTE_SCRIPT_ROOT, basename),
                              capture_out=capture_out)
