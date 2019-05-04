import argparse
import json
import os.path
import shlex
import subprocess
import sys
import time

import mail
import run
import job
import vm
from az import az_resource_group_exists
from utils import (delete_file, exec_sync, get_env, read_file_to_string,
                   write_string_to_file)

DESCRIPTION = "Outsource is a command line tool for running commands remotely."
RESOURCE_GROUP = "outsource-rgsouth"

parser = argparse.ArgumentParser(description=DESCRIPTION)

subparsers = parser.add_subparsers(dest='command_name')

parser_job = subparsers.add_parser('job', help='List, delete, and download data from Outsource jobs.')
parser_job.add_argument('-l', '--list', dest='job_list', action='store_true', help='List Outsource jobs.')
parser_job.add_argument('-d', '--download', dest='job_download', nargs=1, help='Download data from a job\'s VM.')
parser_job.add_argument('-sl', '--show-logs', dest='job_logs', nargs=1, help='Show logs of a job.')
parser_job.add_argument('-s', '--stop', dest='job_stop', nargs=1, help='Stop a job\'s VM.')

parser_vm = subparsers.add_parser('vm', help='Create, list, and delete Outsource VMs.')
parser_vm.add_argument('-c', '--create', dest='vm_create', nargs=2, help='Create a VM [provide: 1) VM name, 2) resource group].')
parser_vm.add_argument('-d', '--delete', dest='vm_delete', nargs=2, help='Delete a VM [provide: 1) VM name, 2) resource group].')
parser_vm.add_argument('-l', '--list', dest='vm_list', action='store_true', help='List VMs and public IP addresses.')

parser_run = subparsers.add_parser('run', help='Outsource a command.')
parser_run.add_argument('-v', '--vm', dest='run_vm', nargs=1,
    help="Run the job on a specific VM. The VM will be created if it does not exist.",
    default=["outsource-vm"])
parser_run.add_argument('-e', '--email', dest='run_email', nargs=1,
    help="Send an email to the specified address when the job completes.",
    default=[""])
parser_run.add_argument('-p', '--ports', dest='run_ports', action='store_true', help="Open all inbound ports to the VM.")
parser_run.add_argument('COMMAND', nargs=argparse.REMAINDER, help="COMMAND")

ARGUMENTS = parser.parse_args()
print(ARGUMENTS)
SUBCOMMAND = ARGUMENTS.command_name

if SUBCOMMAND == None:
    parser.print_help()
    sys.exit(1)

elif SUBCOMMAND == "job":
    try:
        if ARGUMENTS.job_list:
            job.list()
        elif ARGUMENTS.job_download:
            job.download(ARGUMENTS.job_download[0])
        elif ARGUMENTS.job_stop:
            job.stop(ARGUMENTS.job_stop[0])
        elif ARGUMENTS.job_logs:
            job.show_logs(ARGUMENTS.job_logs[0])
        else:
            parser_run.print_help()
    except Exception as e:
        print(e)
        parser_run.print_help()
        sys.exit(1)

elif SUBCOMMAND == "vm":
    try:
        if ARGUMENTS.vm_list:
            vm.list()
        elif ARGUMENTS.vm_delete:
            vm.delete(ARGUMENTS.vm_delete[0], ARGUMENTS.vm_delete[1])
        elif ARGUMENTS.vm_create:
            vm.create(ARGUMENTS.vm_create[0], ARGUMENTS.vm_create[1])
        else:
            parser_run.print_help()
    except Exception as e:
        print(e)
        parser_run.print_help()
        sys.exit(1)

elif SUBCOMMAND == "run":
    SEND_EMAIL_ADDRESS = ARGUMENTS.run_email[0]
    VIRTUAL_MACHINE = ARGUMENTS.run_vm[0]
    OPEN_PORTS = ARGUMENTS.run_ports

    if not ARGUMENTS.COMMAND or len(ARGUMENTS.COMMAND) == 0:
        parser_run.print_help()
        sys.exit(1)

    try:
        run.outsource(ARGUMENTS.COMMAND, RESOURCE_GROUP, VIRTUAL_MACHINE, OPEN_PORTS, SEND_EMAIL_ADDRESS)
    except Exception as e:
        print(e)
        parser_run.print_help()
        sys.exit(1)
