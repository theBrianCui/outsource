from utils import exec_sync, print_stdout
import json

# PLEASE CHANGE THESE VARIABLES ACCORDINGLY. 
rg = "rgsouth12"
vm = "myvm12"

# # az group create --name rgsouth --location southcentralus

exec_sync(["az", "group", "create", "--name", rg, "--location", "southcentralus"],
          "Running echo... ",
          "echo failed!",
          "",
          capture_out=True)

# az vm create --name myvm --resource-group rgsouth --image UbuntuLTS --generate-ssh-keys --size Standard_DS1_v2

exec_sync(["az", "vm", "create", "--name", vm, "--resource-group", rg, "--image", "UbuntuLTS", "--generate-ssh-keys", "--size", "Standard_DS1_v2"],
          "Running echo... ",
          "echo failed!",
          "",
          capture_out=True)

# az vm open-port -g rgsouth -n myvm --port '*'

exec_sync(["az", "vm", "open-port", "-g", rg, "-n", vm, "--port", "*"],
          "Running echo... ",
          "echo failed!",
          "",
          capture_out=True)

# az vm list-ip-addresses --name myvm
output = exec_sync(["az", "vm", "list-ip-addresses", "--name", vm],
          "Running echo... ",
          "echo failed!",
          "",
          capture_out=True)

print("IP:PORT:")
arr = json.loads(output)
ip = arr[0]["virtualMachine"]["network"]["publicIpAddresses"][0]["ipAddress"]
port = 8000
print(str(ip) + ":" + str(port))

# TODO: Make output go to file instead of NULL.
# https://stackoverflow.com/questions/35327623/python-subprocess-run-a-remote-process-in-background-and-immediately-close-the-c
s = exec_sync(["ssh", ip, "-o", "StrictHostKeyChecking=no", "nohup python -m SimpleHTTPServer %d >/dev/null 2>&1 &" % (port)],
          "Running echo... ",
          "echo failed!",
          "",
          capture_out=True)

print(s)