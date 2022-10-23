### The modules used my Emmett to run scans on the Kali box

modules = {
    "nmap" : {
        "cmd" : "nmap -sV -p- -iL /root/Documents/hosts -v -oN /root/Documents/output/nmap/tcp_output",
        "runCount" : 0
    },
    "testssl" : {
        "cmd" : "/bin/bash -c \"cd /root/Documents/output/tls && testssl --warnings=batch --html --json --file ../../hosts && /root/shared/EzModeSSL -d . -o <--CLIENT_NAME-->\"",
        "runCount" : 0
    }
}

# optional arguments for cmd (used to find/replace)
OPTIONAL_ARGS = {
    "<--CLIENT_NAME-->": ""
}


def get_module_info(name, key):
    if is_module(name):
        if key in modules[name]:
            return modules[name][key]

    # will return complete list of modules, whether they are installed or not on the kali box
    return ""

def is_module(name):
    return name in modules

def get_module_cmd(name, optional_args):
    cmd = modules[name]["cmd"]
    print("Raw module command: %s" % cmd)

    for k in optional_args:
        if k in cmd:
            cmd = cmd.replace(k, optional_args[k])

    print("Processed module command: %s" % cmd)
    return cmd


def run_module_requested(name):
    modules[name]["runCount"] += 1

