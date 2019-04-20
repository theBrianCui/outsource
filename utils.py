import sys
import subprocess
import os

def print_stdout(completed_process):
    print(completed_process.stdout.decode("utf-8"), end="")

# Synchronously execute a shell command.
# Exits the script with error code 1 if the command exited with a nonzero code.
def exec_sync(command, before="", error="Something went wrong.", after="Done.",
              capture_out=True, die=True, shell=False):
    if before != "":
        if error: error = " {}".format(error)
        if after: after = " {}".format(after)

    process = None
    stdout = None
    stderr = None

    if capture_out == True:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE

    if before != "": print(before, flush=True)

    try:
        process = subprocess.run(command,
                                 stdout=stdout, stderr=stderr, shell=shell,
                                 check=True)
        if process.returncode != 0:
            raise RuntimeError("Command exited with nonzero return code {}".format(process.returncode))

    except Exception as e:
        error_string = "{}: {}".format(error, e) if error else "{}".format(e)
        print(error_string)
        if die:
            raise RuntimeError(error_string)

    if after: print(after)
    print()

    if process != None and capture_out: return process.stdout.decode("utf-8")
    return ""

def read_file_to_string(filename):
    with open(filename, 'r') as myfile:
        data = myfile.read()
    return data

def get_env(name):
    return os.environ[name]

def write_string_to_file(string, filename):
    with open(filename, "w") as text_file:
        text_file.write(string)

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
