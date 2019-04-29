import json
import subprocess
import sys
import time
import argparse
import shlex
import os.path

import ssh
import email
from utils import (delete_file, exec_sync, get_env, read_file_to_string,
                   write_string_to_file)

DESCRIPTION = "Outsource is a command line tool for running commands remotely."

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('-v', '--vm', nargs=1,
    help="Run the job on a specific VM. The VM will be created if it does not exist.",
    default=["outsource-vm"])

parser.add_argument('-e', '--email', nargs=1, help="Send an email to the specified address when the job completes.")
parser.add_argument('-p', '--ports', action='store_true', help="Open all inbound ports to the VM.")
parser.add_argument('args', nargs=argparse.REMAINDER, help="COMMAND")

subparsers = parser.add_subparsers(dest='command_name')
parser_vm = subparsers.add_parser('vm', help='Create, list, modify and delete Outsource VMs.')
parser_vm.add_argument('--list', dest='vm_list', action='store_true', help='List Outsource VMs and public IP addresses.')

ARGUMENTS = parser.parse_args()
ARGUMENT_ARRAY = tuple(ARGUMENTS.args)
ARGUMENT_PROGRAM = ""               # the base program, e.g. cowsay
ARGUMENT_STRING_FULL = ""           # the full argument string, e.g. cowsay hello world
for arg in ARGUMENT_ARRAY:
    if ARGUMENT_STRING_FULL == "":
        ARGUMENT_PROGRAM = shlex.quote(arg)
        ARGUMENT_STRING_FULL += ARGUMENT_PROGRAM
    else:
        ARGUMENT_STRING_FULL += " {}".format(shlex.quote(arg)) # escape arguments if necessary

# print(ARGUMENTS)
# parser_vm.print_help()
# sys.exit(0)

if len(ARGUMENT_STRING_FULL) == 0:
    parser.print_help()
    sys.exit(1)

# PLEASE CHANGE THESE VARIABLES ACCORDINGLY.
SEND_EMAIL_ADDRESS = ARGUMENTS.email

RESOURCE_GROUP = "outsource-rgsouth"
VIRTUAL_MACHINE = ARGUMENTS.vm[0]

# sys.exit(0)

# # az group create --name rgsouth --location southcentralus

rg_exists = exec_sync("az group exists --name {}".format(RESOURCE_GROUP).split(" "),
            "Checking for existing resource group {}...".format(RESOURCE_GROUP),
            capture_out=True, die=True).strip()

if rg_exists == "true":
    print("The resource group {} already exists.".format(RESOURCE_GROUP))
else:
    exec_sync(["az", "group", "create", "--name", RESOURCE_GROUP, "--location", "southcentralus"],
            "Creating resource group {}...".format(RESOURCE_GROUP),
            capture_out=True, die=True)

vm_list = exec_sync("az vm list -g {}".format(RESOURCE_GROUP).split(" "),
            "Checking for existing VM {}...".format(VIRTUAL_MACHINE))
vm_array = json.loads(vm_list)
vm_exists = False
for vm in vm_array:
    if vm["name"].strip() == VIRTUAL_MACHINE:
        print("VM {} already exists.".format(VIRTUAL_MACHINE))
        vm_exists = True
        break

if not vm_exists:
    # az vm create --name myvm --resource-group rgsouth --image UbuntuLTS --generate-ssh-keys --size Standard_DS1_v2
    exec_sync(["az", "vm", "create", "--name", VIRTUAL_MACHINE, "--resource-group", RESOURCE_GROUP, "--image", "UbuntuLTS", "--generate-ssh-keys", "--size", "Standard_DS1_v2"],
            "Creating virtual machine {}...".format(VIRTUAL_MACHINE),
            capture_out=True)

# az vm open-port -g rgsouth -n myvm --port '*'
if ARGUMENTS.ports:
    exec_sync(["az", "vm", "open-port", "-g", RESOURCE_GROUP, "-n", VIRTUAL_MACHINE, "--port", "*"],
            "Opening ports * ...",
            capture_out=True)

# az vm list-ip-addresses --name myvm
output = exec_sync(["az", "vm", "list-ip-addresses", "--name", VIRTUAL_MACHINE],
          "Getting IP address...",
          capture_out=True)

print("IP:PORT:")
arr = json.loads(output)
ip = arr[0]["virtualMachine"]["network"]["publicIpAddresses"][0]["ipAddress"]
port = 8000
print(str(ip) + ":" + str(port))

if SEND_EMAIL_ADDRESS:
    try:
        ssh.run_remote_script(email.create_email_script(SEND_EMAIL_ADDRESS), ip)
    except Exception as e:
        print(e)

job_name, nohup_script_name, remote_log_name = ssh.create_job(ARGUMENT_STRING_FULL)

# install dependencies
if not ssh.check_remote_program_exists(ip, ARGUMENT_PROGRAM):
    print("{} does not exist on the remote machine.".format(ARGUMENT_PROGRAM))
    print("Attempting install via apt-get...")
    if not ssh.remote_apt_get_program(ip, ARGUMENT_PROGRAM):
        print("Could not install {} via apt-get.".format(ARGUMENT_PROGRAM))
        sys.exit(0)

print("{} program exists".format(ARGUMENT_PROGRAM))

# search for local file dependencies in the command line
for arg in ARGUMENT_ARRAY:
    if os.path.exists(arg) and os.path.isfile(arg):
        print("Found local file dependency: {}".format(arg))
        ssh.upload_job_file(arg, ip, job_name)

ssh.run_remote_script(nohup_script_name, ip)
print("{} job now running, output redirected to {}".format(ARGUMENT_PROGRAM, remote_log_name))

# command = "python -m SimpleHTTPServer 8000"

# ssh.upload_file("monitor.py", ip, "/tmp/outsource/scripts/")
# ssh.run_remote_command(ip, "python /tmp/outsource/scripts/monitor.py " + command, capture_out=True)

# i = 1
# while True:
#      time.sleep(5)
#      process = subprocess.Popen("ssh %s -o StrictHostKeyChecking=no cat /tmp/logs" % (ip), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#      output,stderr = process.communicate()
#      status = process.poll()
#      print("Polling %d:" % (i))
#      print(output)
#      i += 1