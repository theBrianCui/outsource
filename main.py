from utils import exec_sync, print_stdout

a = exec_sync(["echo", "hello"],
              "Running echo...",
              "echo failed!",
              "Done.",
              capture_out=True)

print("process outputted: {}".format(a))


print(exec_sync("az group create --name rgsouth --location southcentralus".split(" "),
                "Running group creation..."))
print(exec_sync("az vm create --name myvm --resource-group rgsouth --image UbuntuLTS --generate-ssh-keys --size Standard_DS1_v2".split(" "),
                "Running VM creation..."))
print(exec_sync("az vm open-port -g rgsouth -n myvm --port *".split(" "),
                "Opening ports..."))
print(exec_sync("az vm list-ip-addresses --name myvm".split(" "),
                "Listing IPs..."))

print("Done.")
