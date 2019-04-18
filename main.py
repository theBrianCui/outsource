from utils import exec_sync, print_stdout
import json
import sys

# PLEASE CHANGE THESE VARIABLES ACCORDINGLY. 
RESOURCE_GROUP = "outsource-rgsouth"
VIRTUAL_MACHINE = "outsource-vm"

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

# TODO: Make output go to file instead of NULL.
# https://stackoverflow.com/questions/35327623/python-subprocess-run-a-remote-process-in-background-and-immediately-close-the-c
s = exec_sync(["ssh", ip, "-o", "StrictHostKeyChecking=no", "lsb_release -a"],
          "Running command on remote VM...",
          capture_out=True)

print(s)