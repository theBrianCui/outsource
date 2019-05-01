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
            (task_id, host, _, command) = line.split(maxsplit=3)
            output = sshtools.run_remote_command(host, "ps aux")
            status = "Running" if command in output else "Finished"
            print('{:<10}{:<17}{:<10}{}'.format(task_id, host, status, command), end="")

def run_fetch_data(task_id):
    # Find host that runs given task
    host = ""
    for line in tasks:
        (t_id, h, _) = line.split(maxsplit=2)
        if t_id == task_id:
            host = h
            break

    # Compress directory in host
    #output = ssh.run_remote_command(host, "")

    print("Fetching data for task no. %s!" % (task_id))


def run_stop(task_id):
    print("Stopping task no. %s!" % (task_id))


DESCRIPTION = "Outsource is a command line tool for running commands remotely."

parser = argparse.ArgumentParser(description=DESCRIPTION)

parser.add_argument('-l', '--list', help="List active tasks.", action="store_true")
parser.add_argument('-f', '--fetch-data', nargs=1, help="Fetch data from task.")
parser.add_argument('-stop', '--stop', nargs=1, help="Stop task.")

ARGUMENTS = parser.parse_args()

if ARGUMENTS.list:
    run_list()
elif ARGUMENTS.fetch_data:
    run_fetch_data(ARGUMENTS.fetch_data[0])
elif ARGUMENTS.stop:
    run_fetch_data(ARGUMENTS.stop[0])
else:
    print("No command")