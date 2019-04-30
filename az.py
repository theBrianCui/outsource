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

def az_vm_list(resource_group, print=False, show_ip=True, silent=True):
    before = ""
    after = ""
    if not silent:
        before = "Listing VMs in resource group {}... ".format(resource_group)
        after = "Done."

    vm_list = exec_sync("az vm list -g {}".format(resource_group).split(" "),
        before=before, after=after, capture_out=True, die=True)

    vm_array = json.loads(vm_list)
    vm_info_list = []

    for vm in vm_array:
        vm_info = {}
        vm_info["name"] = vm["name"].strip()
        vm_info["hardware"] = vm["hardwareProfile"]["vmSize"]
        vm_info["ip"] = ""

        if show_ip:
            vm_info["ip"] = az_vm_get_ip(resource_group, vm_info["name"])

        vm_info_list.append(vm_info)

    return vm_info_list
