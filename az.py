from utils import exec_sync
import json

def az_resource_group_exists(name, create=True, silent=True):
    before = ""
    after = ""
    if not silent:
        before = "Checking for resource group {}... ".format(name)
        after = "Done."

    rg_exists = exec_sync("az group exists --name {}".format(name).split(" "),
                before=before, after=after, capture_out=True, die=True).strip()

    if rg_exists == "true":
        return True
    if not create:
        return False

    before = ""
    after = ""
    if not silent:
        before = "Creating resource group {}...".format(name)
        after = "Done."

    # create the resource group
    exec_sync(["az", "group", "create", "--name", name, "--location", "southcentralus"],
        before=before, after=after, capture_out=True, die=True)

    return az_resource_group_exists(name, create=False, silent=silent)

def az_vm_get_ip(resource_group, vm_name):
    output = exec_sync(["az", "vm", "list-ip-addresses", "-g", resource_group, "--name", vm_name], capture_out=True)
    arr = json.loads(output)
    ip = arr[0]["virtualMachine"]["network"]["publicIpAddresses"][0]["ipAddress"]
    return ip

def az_vm_list(resource_group="", silent=True):
    before = ""
    after = ""
    if not silent:
        before = "Listing VMs... "
        after = "Done."

    command = "az vm list -d"
    if resource_group:
        command += " -g {}".format(resource_group)

    vm_list = exec_sync(command.split(" "), before=before, after=after, capture_out=True, die=True)
    vm_array = json.loads(vm_list)
    vm_info_list = []

    for vm in vm_array:
        vm_info = {}
        vm_info["name"] = vm["name"].strip()
        vm_info["hardware"] = vm["hardwareProfile"]["vmSize"]
        vm_info["resourceGroup"] = vm["resourceGroup"]
        vm_info["ip"] = vm["publicIps"]
        vm_info_list.append(vm_info)

    return vm_info_list

def az_create_vm(resource_group, name, hardware="Standard_DS1_v2", silent=False):
    before = ""
    after = ""
    if not silent:
        before = "Creating virtual machine {} with hardware profile {}...".format(name, hardware)
        after = "Done."

    # az vm create --name myvm --resource-group rgsouth --image UbuntuLTS --generate-ssh-keys --size Standard_DS1_v2
    exec_sync(["az", "vm", "create", "--name", name, "--resource-group", resource_group, "--image", "UbuntuLTS", "--generate-ssh-keys", "--size", hardware],
                before=before, after=after,
                capture_out=True)

    return az_vm_get_ip(resource_group, name)

def is_json(s):
    try:
        json_object = json.loads(s)
    except Exception as e:
        return False
    return True

def is_vm_active(vm_name, resource_group):
    try:
        vm_data = exec_sync(("az vm get-instance-view --name %s --resource-group %s" % (vm_name, resource_group)).split(" "),
            capture_out=True, die=True)
    except Exception as e:
        return False

    if is_json(vm_data):
        vm = json.loads(vm_data)
        return (vm["provisioningState"] == "Succeeded")
    else:
        return False
