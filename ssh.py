import os
from utils import exec_sync, read_file_to_string, write_string_to_file
import time

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
    remote_script_path = "{}{}".format(REMOTE_SCRIPT_ROOT, basename)
    upload_file(script_path, ip, remote_script_path)
    return remote_script_path

def run_remote_script(script_path, ip, capture_out=True):
    print("run remote script")
    remote_script_path = upload_script(script_path, ip)
    return run_remote_command(ip, "bash " + remote_script_path, capture_out=capture_out)

def create_nohup_script(command):
    program_name = command.split(" ")[0]
    file_base_name = "{}_{}".format(program_name, int(time.time()))

    temp_script_name = file_base_name + ".job"
    temp_script_path = "scripts/" + temp_script_name
    temp_log_name = file_base_name + ".log"

    nohup_script = read_file_to_string("scripts/nohup.sh")
    nohup_script = nohup_script.replace("COMMAND_NAME", command)
    nohup_script = nohup_script.replace("LOG_NAME", temp_log_name)

    write_string_to_file(nohup_script, temp_script_path)
    return temp_script_path, temp_log_name
