# Similar to modules, except commands are modular commands that can consist of modules and raw commands
# Take 'engagement' for instance, we can chain multiple tools together

# TODO: switch this to a collection of json files and load from dir
commands = {
    "external" : {
        "modules" : [
            "nmap",
            "testssl"
        ],
        "description": "Runs a collection of modules to perform a basic external test",
    }
}

def get_all_commands_info():
    return commands


def get_command_info(name, key):
    if is_command(name):
        if key in commands[name]:
            return commands[name][key]

    return ""


def is_command(name):
    return name in commands


def get_command_modules(name):
    return commands[name]["modules"]