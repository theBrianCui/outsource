import subprocess
import sys

command = " ".join(sys.argv[1:])

process = subprocess.Popen("nohup " + command + " >/tmp/logs 2>&1 &", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)