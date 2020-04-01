import xlrd

def parseGeneralInfo(inventory_file):
    configuration_variable_mappers = {"CVP IP Addresses": "cvp_instance_ips", "CVP Ingest Auth Key": "cvp_ingestauth_key",
    "Management Gateway":"mgmt_gateway",  "DNS Servers":"name_servers", "NTP Servers": "ntp_servers",
    "cvpadmin password sha512 hash":"cvpadmin_pass", "admin password sha512 hash":"admin_pass"}

    workbook = xlrd.open_workbook(inventory_file)
    info_worksheet = workbook.sheet_by_name("General Configuration Details")
    info = {}
    # transform the workbook to a list of dictionaries
    for row in range(1, info_worksheet.nrows):
        k, v = info_worksheet.cell_value(row,0), info_worksheet.cell_value(row,1)
        if k in configuration_variable_mappers.keys():
            info[configuration_variable_mappers[k]] = v
    general_info = {}
    general_info["local_users"] = {
        "admin": {
            "privilege": 15,
            "role": "network-admin",
            "sha512_password": info["admin_pass"]
        },
        "cvpadmin":{
            "privilege": 15,
            "role": "network-admin",
            "sha512_password": info["cvpadmin_pass"]
        }
    }
    general_info["cvp_instance_ips"] = [ip.strip() for ip in info["cvp_instance_ips"].split(",") if ip != ""]

    general_info["cvp_ingestauth_key"] = info["cvp_ingestauth_key"] if info["cvp_ingestauth_key"] != "" else None
    general_info["mgmt_gateway"] = info["mgmt_gateway"]
    general_info["name_servers"] = [ip.strip() for ip in info["name_servers"].split(",") if ip != ""]
    general_info["ntp_servers"] = [ip.strip() for ip in info["ntp_servers"].split(",") if ip != ""]
    return general_info

def generateGroupVarsAll(inventory_file):
    return parseGeneralInfo(inventory_file)