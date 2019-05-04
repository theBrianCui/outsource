import json
import subprocess
import sys
import time
import argparse
import shlex

import sshtools
import mail
from utils import (delete_file, exec_sync, get_env, read_file_to_string,
                   write_string_to_file)
import az
import tabulate

def list():
    vm_list = exec_sync("az vm list -d".split(" "), capture_out=True, die=True)
    vm_array = json.loads(vm_list)
    vm_table = [["VM Name", "Resource Group", "Public IP Address"]]

    for vm in vm_array:
        vm_table.append([vm["name"], vm["resourceGroup"], vm["publicIps"]])

    print(tabulate.tabulate(vm_table, headers="firstrow"))

def delete(vm_name, resource_group):
    print("Stopping VM %s" % vm_name)
    exec_sync(["az", "vm", "delete", "-g", resource_group, "-n", vm_name, "--yes"],
               "Stopping VM ...",
               capture_out=True)
    print("Successfully stopped VM %s!" % vm_name)

def create(vm_name, resource_group):
    az.az_resource_group_exists(resource_group, silent=False)
    az.az_create_vm(resource_group, vm_name)
