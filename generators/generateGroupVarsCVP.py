
def generateGroupVarsCVP(inventory_file):
    variables = {
        "ansible_connection": "httpapi",
        "ansible_http_api_use_ssl": True,
        "ansible_httpapi_validate_certs": False,
        "ansible_user": "cvpadmin",
        "ansible_network_os": "eos",
        "ansible_httpapi_port": 443,
        "ansible_python_interpreter": "$(which python)"
    }
    return variables

