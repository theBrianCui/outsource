# outsource
outsource your job to the cloud

## Installation

First, install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) and login with `az login`.

Clone the repository, create a virtual environment, and install requirements:

```
git clone git@github.com:theBrianCui/outsource.git
cd outsource
virtualenv --python=python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

The easiest way to use outsource is by creating an alias to run the `main.py` script.

```
alias outsource="python3 ~/workspace/outsource/main.py"
```

The default Azure resource group name is `outsource-rgsouth`; it can be defined by the `OUTSOURCE_RESOURCE_GROUP` environmental variable.

To get email notifications, you will need a [SendGrid API key](https://sendgrid.com/). SendGrid offers a free email sending for up to 100 emails/day. The key is read from the `SENDGRID_API_KEY` environmental variable; you can assign one like so.

```
export SENDGRID_API_KEY='1234ABCD'
```
## Examples

### Hello World

```
outsource run cowsay hello world
```

### Hello World with email notification

```
outsource run -e name@mail.com cowsay hello world
```

### Compile a Program

```
outsource run -e name@mail.com gcc --verbose hello.c -o hello
```

### Expose Ports and Run a Webserver

```
outsource run -p python -m SimpleHTTPServer
```

### List VMs

```
outsource vm --list
```

### Get Help

```
outsource vm --help
```
