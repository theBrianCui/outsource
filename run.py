import sys
import json
import shlex
import os

import az
from utils import exec_sync, add_job_to_list
import sshtools

def outsource(arguments, resource_group, virtual_machine, open_ports=False, email=""):
    ARGUMENT_ARRAY = tuple(arguments)
    ARGUMENT_PROGRAM = ""               # the base program, e.g. cowsay
    ARGUMENT_STRING_FULL = ""           # the full argument string, e.g. cowsay hello world
    for arg in ARGUMENT_ARRAY:
        if ARGUMENT_STRING_FULL == "":
            ARGUMENT_PROGRAM = shlex.quote(arg)
            ARGUMENT_STRING_FULL += ARGUMENT_PROGRAM
        else:
            ARGUMENT_STRING_FULL += " {}".format(shlex.quote(arg)) # escape arguments if necessary
    
    if len(ARGUMENT_STRING_FULL) == 0:
        raise RuntimeError("Arguments are empty.")

    # # az group create --name rgsouth --location southcentralus
    if not az.az_resource_group_exists(resource_group, create=True, silent=False):
        raise RuntimeError("FATAL: Could not create resource group {}".format(resource_group))

    vm_list = az.az_vm_list(resource_group)
    vm_exists = False
    vm_ip = ""
    for vm in vm_list:
        if vm["name"] == virtual_machine:
            vm_exists = True
            vm_ip = vm["ip"]
            break

    if not vm_exists:
        vm_ip = az.az_create_vm(resource_group, virtual_machine)
        vm_exists = True

    # az vm open-port -g rgsouth -n myvm --port '*'
    if open_ports:
        exec_sync(["az", "vm", "open-port", "-g", resource_group, "-n", virtual_machine, "--port", "*"],
                "Opening ports * ...",
                capture_out=True)

    print("{} IP: {}".format(virtual_machine, vm_ip))

    if email:
        try:
            sshtools.run_remote_script(email.create_email_script(email), vm_ip)
        except Exception as e:
            print("Could not set up email: {}".format(e))

    job_name, nohup_script_name, remote_log_name = sshtools.create_job(ARGUMENT_STRING_FULL)

    # install dependencies
    if not sshtools.check_remote_program_exists(vm_ip, ARGUMENT_PROGRAM):
        print("{} does not exist on the remote machine.".format(ARGUMENT_PROGRAM))
        print("Attempting install via apt-get...")
        if not sshtools.remote_apt_get_program(vm_ip, ARGUMENT_PROGRAM):
            print("Could not install {} via apt-get.".format(ARGUMENT_PROGRAM))
            sys.exit(0)

    print("{} program exists".format(ARGUMENT_PROGRAM))

    # search for local file dependencies in the command line
    for arg in ARGUMENT_ARRAY:
        if os.path.exists(arg) and os.path.isfile(arg):
            print("Found local file dependency: {}".format(arg))
            sshtools.upload_job_file(arg, vm_ip, job_name)

    pid = sshtools.run_remote_script(nohup_script_name, vm_ip)
    pid = pid[1:-1]
    print("{} job now running, output redirected to {}".format(ARGUMENT_PROGRAM, remote_log_name))
    
    add_job_to_list(vm_ip, ARGUMENT_STRING_FULL, job_name, pid, virtual_machine, resource_group)
