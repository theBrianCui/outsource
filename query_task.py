import json
import subprocess
import sys
import time
import argparse
import shlex

import ssh
import email
from utils import (delete_file, exec_sync, get_env, read_file_to_string,
                   write_string_to_file)

def run_list():
    tasks = open("tasks", "r")
    print('{:<17}{:<10}{}'.format("Host", "Status", "Command"))
    for line in tasks:
        (host, command) = line.split(maxsplit=1)
        output = ssh.run_remote_command(host, "ps aux")
        status = "Running" if command in output else "Finished"
        print('{:<17}{:<10}{}'.format(host, status, command), end="")


def run_fetch_data(task_id):
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