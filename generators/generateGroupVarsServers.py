import xlrd

def generateGroupVarsServers(inventory_file):
    servers = {}
    servers["servers"] = parseServers(inventory_file)
    servers["port_profiles"] = parsePortProfiles(inventory_file)
    return servers

def parseServers(inventory_file):
    servers = {}
    workbook = xlrd.open_workbook(inventory_file)
    servers_worksheet = workbook.sheet_by_name("Servers")
    first_row = [] # The row where we stock the name of the column
    for col in range(servers_worksheet.ncols):
        first_row.append( servers_worksheet.cell_value(0,col) )
    # transform the workbook to a list of dictionaries
    for row in range(1, servers_worksheet.nrows):
        server_info = {}
        for col in range(servers_worksheet.ncols):
            server_info[first_row[col]]=servers_worksheet.cell_value(row,col)
        server_name = server_info["Server"]
        if server_name not in servers:
            servers[server_name] = {}
        servers[server_name]["rack"] = server_info["Rack"]
        adapter_info = {
            "server_ports": [ port.strip() for port in server_info["Server Ports"].split(",") ],
            "switch_ports": [ port.strip() for port in server_info["Switch Ports"].split(",") ],
            "switches": [ switch.strip() for switch in server_info["Switches"].split(",") ],
            "profile": server_info["Port Profile"]
        }
        if server_info["Port-Channel"].strip() != "":
            adapter_info["port_channel"] = {
                "state": "present",
                "description": server_info["Port-Channel"].strip(),
                "mode": server_info["Port-Channel Mode"]
            }
        
        if "adapters" not in servers[server_name]:
            servers[server_name]["adapters"] = []
        servers[server_name]["adapters"].append(adapter_info)
    return servers

def parsePortProfiles(inventory_file):
    port_profiles = {}
    workbook = xlrd.open_workbook(inventory_file)
    port_profile_worksheet = workbook.sheet_by_name("Port Profiles")
    first_row = [] # The row where we stock the name of the column
    for col in range(port_profile_worksheet.ncols):
        first_row.append( port_profile_worksheet.cell_value(0,col) )
    # transform the workbook to a list of dictionaries
    for row in range(1, port_profile_worksheet.nrows):
        port_profile_info = {}
        for col in range(port_profile_worksheet.ncols):
            port_profile_info[first_row[col]]=port_profile_worksheet.cell_value(row,col)

        port_profile_name = port_profile_info["Port Profile"]
        mode = port_profile_info["Mode"]
        try:
            vlans = str(int(port_profile_info["Vlans"]))
        except:
            vlans = str(port_profile_info["Vlans"])
        port_profiles[port_profile_name] = {
            "mode": mode,
            "vlans": vlans
        }
    return port_profiles