from utils import exec_sync, print_stdout

a = exec_sync(["echo", "hello"],
              "Running echo... ",
              "echo failed!",
              "Done.",
              capture_out=True)

print("process outputted: {}".format(a))
