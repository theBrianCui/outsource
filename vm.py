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

def list():
    print("List VMs")

def delete(vm):
    print("Delete " + vm)

def create(vm):
    print("Create " + vm)
