import sys
import json
import shlex
import os

from az import az_resource_group_exists
from utils import exec_sync
import ssh

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
    if not az_resource_group_exists(resource_group, create=True, silent=False):
        raise RuntimeError("FATAL: Could not create resource group {}".format(resource_group))

    vm_list = exec_sync("az vm list -g {}".format(resource_group).split(" "),
                "Checking for existing VM {}...".format(virtual_machine))
    vm_array = json.loads(vm_list)
    vm_exists = False
    for vm in vm_array:
        if vm["name"].strip() == virtual_machine:
            print("VM {} already exists.".format(virtual_machine))
            vm_exists = True
            break

    if not vm_exists:
        # az vm create --name myvm --resource-group rgsouth --image UbuntuLTS --generate-ssh-keys --size Standard_DS1_v2
        exec_sync(["az", "vm", "create", "--name", virtual_machine, "--resource-group", resource_group, "--image", "UbuntuLTS", "--generate-ssh-keys", "--size", "Standard_DS1_v2"],
                "Creating virtual machine {}...".format(virtual_machine),
                capture_out=True)

    # az vm open-port -g rgsouth -n myvm --port '*'
    if open_ports:
        exec_sync(["az", "vm", "open-port", "-g", resource_group, "-n", virtual_machine, "--port", "*"],
                "Opening ports * ...",
                capture_out=True)

    # az vm list-ip-addresses --name myvm
    output = exec_sync(["az", "vm", "list-ip-addresses", "--name", virtual_machine],
            "Getting IP address...",
            capture_out=True)

    print("IP:PORT:")
    arr = json.loads(output)
    ip = arr[0]["virtualMachine"]["network"]["publicIpAddresses"][0]["ipAddress"]
    port = 8000
    print(str(ip) + ":" + str(port))

    if email:
        try:
            ssh.run_remote_script(email.create_email_script(email), ip)
        except Exception as e:
            print("Could not set up email: {}".format(e))

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
