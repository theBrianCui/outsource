from utils import exec_sync, print_stdout

exec_sync(["echo", "hello"],
          "Running echo... ",
          "echo failed!",
          "Done.",
          silent=False)
