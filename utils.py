import sys
import subprocess

def print_stdout(completed_process):
    print(completed_process.stdout.decode("utf-8"), end="")

# Synchronously execute a shell command.
# Exits the script with error code 1 if the command exited with a nonzero code.
def exec_sync(command, before="", error="", after="",
              capture_out=True, capture_err=False, die=True):

    process = None
    stdout = None
    stderr = None

    if capture_out == True: stdout = subprocess.PIPE
    if capture_err == True: stderr = subprocess.PIPE
    if before != "": print(before, end="", flush=True)

    try:
        process = subprocess.run(command,
                                 stdout=stdout, stderr=stderr,
                                 check=True)
    except Exception as e:
        if die:
            raise RuntimeError(error)
        else:
            print(error)

    if after != "": print(after)
    if process != None and (capture_out or capture_err): return process.stdout.decode("utf-8")
    return ""
