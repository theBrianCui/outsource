from utils import exec_sync, read_file_to_string, get_env, delete_file, write_string_to_file
import json
import time
import subprocess
import sys
import ssh

# PLEASE CHANGE THESE VARIABLES ACCORDINGLY.
SEND_EMAIL = False
SEND_EMAIL_ADDRESS = "brianzcui" + "@gmail.com"
SEND_EMAIL_SCRIPT = "scripts/email.sh"

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

if SEND_EMAIL and get_env("SENDGRID_API_KEY"):
    print("Preparing email send script...")
    email_script = read_file_to_string(SEND_EMAIL_SCRIPT)
    email_script = email_script.replace("SENDGRID_API_KEY", get_env("SENDGRID_API_KEY"))
    email_script = email_script.replace("RECIPIENT", SEND_EMAIL_ADDRESS)
    email_script = email_script.replace("SUBJECT", "Hello from Outsource Script!")
    email_script = email_script.replace("BODY", "Hello from Outsource!")
    delete_file(SEND_EMAIL_SCRIPT + ".tmp")
    write_string_to_file(email_script, SEND_EMAIL_SCRIPT + ".tmp")

    print(read_file_to_string(SEND_EMAIL_SCRIPT + ".tmp"))
    print("Sending email on remote server...")
    ssh.run_remote_script("{}.tmp", ip)
    # subprocess.call('ssh {} -o StrictHostKeyChecking=no "bash -s" < {}.tmp'.format(ip, SEND_EMAIL_SCRIPT), shell=True)

sys.exit(0)

# TODO: Make output go to file instead of NULL.
# https://stackoverflow.com/questions/35327623/python-subprocess-run-a-remote-process-in-background-and-immediately-close-the-c

# ["ssh", ip, "-o", "StrictHostKeyChecking=no", "nohup python -m SimpleHTTPServer %d >/home/msf1013/logs 2>&1 &" % (port)]
s = exec_sync(["ssh", ip, "-o", "StrictHostKeyChecking=no", "nohup python -m SimpleHTTPServer %d >/tmp/logs 2>&1 &" % (port)],
          "Running echo... ",
          "echo failed!",
          "",
          capture_out=True)

i = 1
while True:
     time.sleep(5)
     process = subprocess.Popen("ssh %s -o StrictHostKeyChecking=no cat /tmp/logs" % (ip), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
     output,stderr = process.communicate()
     status = process.poll()
     print("Polling %d:" % (i))
     print(output)
     i += 1