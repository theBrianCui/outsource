from utils import exec_sync, read_file_to_string, get_env, delete_file, write_string_to_file
import email
import json
import time
import subprocess
import sys
import ssh

# PLEASE CHANGE THESE VARIABLES ACCORDINGLY.
SEND_EMAIL = False
SEND_EMAIL_ADDRESS = "brianzcui" + "@gmail.com"
SEND_EMAIL_SCRIPT = "scripts/email.sh"

RESOURCE_GROUP = "outsource-rgsouth-1"
VIRTUAL_MACHINE = "outsource-vm-1"

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

if SEND_EMAIL:
    try:
        ssh.run_remote_script(email.create_email_script(SEND_EMAIL_ADDRESS), ip)
    except Exception as e:
        print(e)

command = "python -m SimpleHTTPServer 8000"

ssh.upload_file("monitor.py", ip, "/tmp/outsource/scripts/")
ssh.run_remote_command(ip, "python /tmp/outsource/scripts/monitor.py " + command, capture_out=True)

i = 1
while True:
     time.sleep(5)
     process = subprocess.Popen("ssh %s -o StrictHostKeyChecking=no cat /tmp/logs" % (ip), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
     output,stderr = process.communicate()
     status = process.poll()
     print("Polling %d:" % (i))
     print(output)
     i += 1