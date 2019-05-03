import os
from utils import exec_sync, read_file_to_string, write_string_to_file
import time

REMOTE_JOB_ROOT = "/tmp/outsource/jobs/"
REMOTE_SCRIPT_ROOT = "/tmp/outsource/scripts/"

def run_remote_command(ip, command, capture_out=True):
    #print("run remote command {}".format(command))
    output = exec_sync('ssh {} -o StrictHostKeyChecking=no "{} & echo $!"'.format(ip, command),
                       capture_out=capture_out, shell=True, after=None)
    return output

def check_remote_program_exists(ip, program):
    print("remote check program exists {}".format(program))
    remote_command_path = run_remote_command(ip, "command -v {} || true".format(program), capture_out=True)
    print("remote command path: {}".format(remote_command_path))
    return remote_command_path.strip() != ""

def remote_apt_get_program(ip, program):
    print("remote apt get")
    try:
        run_remote_command(ip, "sudo apt-get install -y {}".format(program))
    except Exception:
        pass
    return check_remote_program_exists(ip, program)

def get_local_user():
    print("get local user")
    current_user = exec_sync(["whoami"], "", "", "")
    return current_user.strip()

def upload_file(local_path, ip, dest_path):
    print("upload file")
    dirname = os.path.dirname(dest_path)
    run_remote_command(ip, "mkdir -p {}".format(dirname))
    exec_sync("scp -r {} {}@{}:{}".format(local_path, get_local_user(), ip, dest_path),
              capture_out=False, shell=True)

def upload_job_file(local_path, ip, jobname):
    print("upload job file")
    dirname = "{}{}/".format(REMOTE_JOB_ROOT, jobname)
    filename = os.path.basename(local_path)
    upload_file(local_path, ip, dirname + filename)

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

def create_job(command):
    program_name = command.split(" ")[0]
    job_name = "{}_{}".format(program_name, int(time.time()))

    temp_script_name = job_name + ".job"
    temp_script_path = "scripts/" + temp_script_name
    temp_log_name = job_name + ".log"

    nohup_script = read_file_to_string("scripts/nohup.sh")
    nohup_script = nohup_script.replace("JOB_NAME", job_name)
    nohup_script = nohup_script.replace("COMMAND_NAME", command)
    nohup_script = nohup_script.replace("LOG_NAME", temp_log_name)

    write_string_to_file(nohup_script, temp_script_path)
    return job_name, temp_script_path, temp_log_name
