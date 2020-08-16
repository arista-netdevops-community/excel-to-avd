
def generateGroupVarsCVP(inventory_file, cvpadmin_password):
    variables = {
        "ansible_connection": "httpapi",
        "ansible_http_api_use_ssl": True,
        "ansible_httpapi_validate_certs": False,
        "ansible_user": "cvpadmin",
        "ansible_password": cvpadmin_password,
        "ansible_network_os": "eos",
        "ansible_httpapi_port": 443,
        "ansible_python_interpreter": "$(which python)"
    }
    return variables

