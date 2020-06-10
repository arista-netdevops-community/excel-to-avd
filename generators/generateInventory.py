import xlrd
import yaml

def getFabricName(inventory_file):
    workbook = xlrd.open_workbook(inventory_file)
    info_worksheet = workbook.sheet_by_name("General Configuration Details")
    # transform the workbook to a list of dictionaries
    for row in range(1, info_worksheet.nrows):
        k, v = info_worksheet.cell_value(row,0), info_worksheet.cell_value(row,1)
        if k == "Fabric Name":
            v = v if v != "" else None
            return v
    return None

def getCVPAddresses(inventory_file):
    workbook = xlrd.open_workbook(inventory_file)
    info_worksheet = workbook.sheet_by_name("General Configuration Details")
    # transform the workbook to a list of dictionaries
    for row in range(1, info_worksheet.nrows):
        k, v = info_worksheet.cell_value(row,0), info_worksheet.cell_value(row,1)
        if k == "CVP IP Addresses":
            return [ip.strip() for ip in v.split(",") if ip != ""]
    return None

def getCVPInventory(inventory_file):
    cvp_addresses = getCVPAddresses(inventory_file)
    cvp_dict = {"hosts": {}}
    cvp_node_names = ["cvp_primary", "cvp_secondary", "cvp_tertiary"]
    for i, address in enumerate(cvp_addresses):
        cvp_dict["hosts"][cvp_node_names[i]] = {
            "ansible_httpapi_host": address,
            "ansible_host": address
        }
        break
    return cvp_dict

def parseSpineInfo(inventory_file):
    '''
    '''
    spines_info = {"hosts": {}}
    workbook = xlrd.open_workbook(inventory_file)
    inventory_worksheet = workbook.sheet_by_name("Spine Info")
    node_groups = {}
    first_row = [] # The row where we stock the name of the column
    for col in range(inventory_worksheet.ncols):
        first_row.append( inventory_worksheet.cell_value(0,col) )
    # transform the workbook to a list of dictionaries
    for row in range(1, inventory_worksheet.nrows):
        spine_info = {}
        for col in range(inventory_worksheet.ncols):
            spine_info[first_row[col]]=inventory_worksheet.cell_value(row,col)
        hostname = spine_info["Hostname"]
        spines_info["hosts"][hostname] = {"ansible_host": spine_info["Management IP"].split("/")[0]}
    return spines_info

def parseLeafInfo(inventory_file, leaf_type="L3"):
    '''
    type: options are 'L3' or 'L2'
    '''
    leafs = {}
    workbook = xlrd.open_workbook(inventory_file)
    sheetname = "L3 Leaf Info" if leaf_type == "L3" else "L2 Leaf Info"
    inventory_worksheet = workbook.sheet_by_name(sheetname)
    node_groups = {}
    first_row = [] # The row where we stock the name of the column
    for col in range(inventory_worksheet.ncols):
        first_row.append( inventory_worksheet.cell_value(0,col) )
    # transform the workbook to a list of dictionaries
    for row in range(1, inventory_worksheet.nrows):
        leaf_info = {}
        for col in range(inventory_worksheet.ncols):
            leaf_info[first_row[col]]=inventory_worksheet.cell_value(row,col)
        hostname = leaf_info["Hostname"]
        node_details = {}
        node_details["ansible_host"] = leaf_info["Management IP"].split("/")[0]
        if leaf_info["Container Name"] not in node_groups.keys():
            node_groups[leaf_info["Container Name"]] = {"hosts": {hostname: node_details}}
        else:
            node_groups[leaf_info["Container Name"]]["hosts"][hostname] = node_details
    leafs["children"] = node_groups
    return leafs

def getServers():
    servers = {"children": {"L3_LEAFS": None, "L2_LEAFS": None}}
    return servers

def getTenantNetworks():
    tn = {"children": {"L3_LEAFS": None, "L2_LEAFS": None}}
    return tn

def getFabricInventory(inventory_file):
    fabric_inventory = {"children":{}}
    fabric_inventory["children"]["SPINES"] = parseSpineInfo(inventory_file)
    fabric_inventory["children"]["L3_LEAFS"] = parseLeafInfo(inventory_file, leaf_type="L3")
    fabric_inventory["children"]["L2_LEAFS"] = parseLeafInfo(inventory_file, leaf_type="L2")
    fabric_inventory["vars"] = {
        "ansible_connection": "httpapi",
        "ansible_network_os": "eos",
        "ansible_become": "yes",
        "ansible_become_method": "enable",
        "ansible_httpapi_use_ssl": True,
        "ansible_httpapi_validate_certs": False
    }
    return fabric_inventory

def generateInventory(inventory_file):
    fabric_name = getFabricName(inventory_file)
    if fabric_name is None:
        return
    inventory = {"all":{"children":{
        "CVP": None,
        fabric_name: None
    }}}
    #Add CVP info
    inventory["all"]["children"]["CVP"] = getCVPInventory(inventory_file)

    #Add Fabric info
    inventory["all"]["children"][fabric_name] = getFabricInventory(inventory_file)

    #Add Servers
    inventory["all"]["children"]["SERVERS"] = getServers()

    #Add Tenant Networks
    inventory["all"]["children"]["TENANT_NETWORKS"] = getTenantNetworks()

    return inventory

if __name__ == "__main__":
    generateInventory("PotentialAnsibleCSVTemplate.xlsx")