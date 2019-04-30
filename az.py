from utils import exec_sync

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
