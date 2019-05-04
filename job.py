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
from az import is_vm_active
import tabulate

def list():
    with open("scripts/jobs", "r") as file:
        lines = file.readlines()

    with open("scripts/jobs", "w") as file:
        jobs_table =[["Task ID", "IP Address", "VM Name", "Status", "Command"]]
        for line in lines:
            (task_id, host, _, _, vm_name, resource_group, command) = line.split(maxsplit=6)
            # Prune tasks that aren't reachable
            if is_vm_active(vm_name, resource_group):
                output = sshtools.run_remote_command(host, "ps aux")
                status = "Running" if command in output else "Finished"
                jobs_table.append([task_id, host, vm_name, status, command])
                file.write(line)
        print(tabulate.tabulate(jobs_table, headers="firstrow"))

def download(task_id):
    # Find host that runs given task
    host = ""
    job_name = ""
    vm_name = ""
    resource_group = ""
    with open("scripts/jobs", "r") as file:
        for line in file:
            (t_id, h, job_name, _, vm_name, resource_group, _) = line.split(maxsplit=6)
            if t_id == task_id:
                host = h
                break

    # Verify that task exists
    if host == "":
        print("Task no. %s not found." % task_id)
        return

    # Download data only if VM is still running
    if is_vm_active(vm_name, resource_group):
        # Compress task's directory in VM
        print("Fetching data from task no. %s!" % (task_id))
        output = sshtools.run_remote_command(host,
            "tar -C /tmp/outsource/jobs -cvf /tmp/outsource/jobs/task_%s.gz.tar %s" % (task_id, job_name))

        # Transfer .zip to host
        process = subprocess.Popen("scp %s:/tmp/outsource/jobs/task_%s.gz.tar task_%s.gz.tar" %
            (host, task_id, task_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print("Successfully downloaded data from task no. %s in task_%s.gz.tar!" % (task_id, task_id))
    else:
        print("Couldn't download task's data: VM is no longer active.")
        return

def stop(task_id):
    with open("scripts/jobs", "r") as file:
        lines = file.readlines()

    stopped_task = False

    with open("scripts/jobs", "w") as file:
        for line in lines:
            (t_id, host, _, pid, vm_name, resource_group, _) = line.split(maxsplit=6)
            if t_id == task_id and is_vm_active(vm_name, resource_group):
                print("Stopping task no. %s!" % (task_id))
                if pid != "-1":
                    sshtools.run_remote_command(host, "kill %s" % pid)
                print("Successfully stopped task no. %s!" % (task_id))
                stopped_task = True
            else:
                file.write(line)
    
    if not stopped_task:
        print("Couldn't stop task no. %s: either the task doesn't exist or its VM is no longer active." % task_id)

def show_logs(task_id):
    # Find host that runs given task
    host = ""
    job_name = ""
    vm_name = ""
    resource_group = ""

    with open("scripts/jobs", "r") as file:
        for line in file:
            (t_id, h, job_name, pid, vm_name, resource_group, _) = line.split(maxsplit=6)
            if t_id == task_id:
                host = h
                break

    # Verify that task exists
    if host == "":
        print("Task no. %s not found." % task_id)
        return

    # Download data only if VM is still running
    if is_vm_active(vm_name, resource_group):
        # Transfer log file to host
        process = subprocess.Popen("scp %s:/tmp/outsource/logs/%s.log task_%s.log" %
            (host, job_name, task_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print("Successfully downloaded logs from task no. %s in task_%s.log!" % (task_id, task_id))
    else:
        print("Couldn't download task's logs: VM is no longer active.")
        return
