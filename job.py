import json
import subprocess
import sys
import time
import argparse
import shlex

import sshtools
import mail
from utils import (delete_file, exec_sync, get_env, read_file_to_string,
                   write_string_to_file)

def list():
    with open("scripts/jobs", "r") as file:
        print('{:<10}{:<17}{:<10}{}'.format("Task_ID", "Host", "Status", "Command"))
        for line in file:
            (task_id, host, _, _, _, _, command) = line.split(maxsplit=6)
            output = sshtools.run_remote_command(host, "ps aux")
            status = "Running" if command in output else "Finished"
            print('{:<10}{:<17}{:<10}{}'.format(task_id, host, status, command), end="")

def download(task_id):
    # Find host that runs given task
    host = ""
    job_name = ""
    with open("scripts/jobs", "r") as file:
        for line in file:
            (t_id, h, job_name, _) = line.split(maxsplit=3)
            if t_id == task_id:
                host = h
                break

    # Compress task's directory in VM
    print("Fetching data from task no. %s!" % (task_id))
    output = sshtools.run_remote_command(host,
        "tar -C /tmp/outsource/jobs -cvf /tmp/outsource/jobs/task_%s.gz.tar %s" % (task_id, job_name))

    # Transfer .zip to host
    process = subprocess.Popen("scp %s:/tmp/outsource/jobs/task_%s.gz.tar task_%s.gz.tar" %
        (host, task_id, task_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("Successfully downloaded data from task no. %s in task_%s.gz.tar!" % (task_id, task_id))

def stop(task_id):
    print("Stopping task no. %s!" % (task_id))

    with open("scripts/jobs", "r") as file:
        lines = file.readlines()

    with open("scripts/jobs", "w") as file:
        for line in lines:
            (t_id, host, _, pid, _) = line.split(maxsplit=4)
            if t_id == task_id:
                sshtools.run_remote_command(host, "kill %s" % pid)
            else:
                file.write(line)
    print("Successfully stopped task no. %s!" % (task_id))

def show_logs(task_id):
    # Find host that runs given task
    host = ""
    job_name = ""
    with open("scripts/jobs", "r") as file:
        for line in file:
            (t_id, h, job_name, _) = line.split(maxsplit=3)
            if t_id == task_id:
                host = h
                break

    # Transfer log file to host
    process = subprocess.Popen("scp %s:/tmp/outsource/logs/%s.log task_%s.log" %
        (host, job_name, task_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("Successfully downloaded logs from task no. %s in task_%s.log!" % (task_id, task_id))

