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

def run_list():
    with open("scripts/jobs", "r") as file:
        print('{:<10}{:<17}{:<10}{}'.format("Task_ID", "Host", "Status", "Command"))
        for line in file:
            (task_id, host, _, _, _, command) = line.split(maxsplit=5)
            output = sshtools.run_remote_command(host, "ps aux")
            status = "Running" if command in output else "Finished"
            print('{:<10}{:<17}{:<10}{}'.format(task_id, host, status, command), end="")

def run_fetch_data(task_id):
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
    print("Fetching data for task no. %s!" % (task_id))
    output = sshtools.run_remote_command(host, "tar -C /tmp/outsource/jobs -cvf /tmp/outsource/jobs/task_%s.gz.tar %s" % (task_id, job_name))

    # Transfer .zip to host
    process = subprocess.Popen("scp %s:/tmp/outsource/jobs/task_%s.gz.tar task_%s.gz.tar" % (host, task_id, task_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("Successfully downloaded data from task no. %s in task_%s.gz.tar!" % (task_id, task_id))


def run_stop(task_id):
    print("Stopping task no. %s!" % (task_id))

    with open("scripts/jobs", "r") as file:
        lines = file.readlines()

    with open("scripts/jobs", "w") as file:
        for line in lines:
            (t_id, _, _, vm_name, resource_group, _) = line.split(maxsplit=5)
            if t_id == task_id:
                exec_sync(["az", "vm", "delete", "-g", resource_group, "-n", vm_name, "--yes"],
                           "Stopping VM ...",
                           capture_out=True)
            else:
                file.write(line)
    print("Successfully stopped task no. %s!" % (task_id))

DESCRIPTION = "Outsource is a command line tool for running commands remotely."

parser = argparse.ArgumentParser(description=DESCRIPTION)

parser.add_argument('-l', '--list', help="List active tasks.", action="store_true")
parser.add_argument('-f', '--fetch-data', nargs=1, help="Fetch data from task.")
parser.add_argument('-s', '--stop', nargs=1, help="Stop task.")

ARGUMENTS = parser.parse_args()

if ARGUMENTS.list:
    run_list()
elif ARGUMENTS.fetch_data:
    run_fetch_data(ARGUMENTS.fetch_data[0])
elif ARGUMENTS.stop:
    run_stop(ARGUMENTS.stop[0])
else:
    print("No command")
