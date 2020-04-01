import xlrd
import json, yaml, re
from collections import OrderedDict

def convertToBoolIfNeeded(variable):
    if type(variable) == str and re.match(r'(?i)(True|False)', variable.strip()):
        variable = True if re.match(r'(?i)true', variable.strip()) else False
    return variable

def convertToList(variable):
    if type(variable) == str and "," in variable:
        variable = [v.strip() for v in variable.split(",") if v != ""]
    return variable

def consolidateNodeGroups(node_groups):
    node_group_level_vars = ["bgp_as", "platform", "filter", "parent_l3leafs", "uplink_interfaces"]
    groups_names = node_groups.keys()
    new_group_vars = {}
    for group, nodes in node_groups.items():
        new_group_vars[group] = {}
        for node, details in nodes.items():               
            if len(details.keys()) > 1:
                host1_vars = details[list(details.keys())[0]]
                host2_vars = details[list(details.keys())[1]]
                for variable, value in host1_vars.items():
                    if variable in host2_vars.keys() and host1_vars[variable] == host2_vars[variable]:                        
                        new_group_vars[group][variable] = value
                    elif variable in node_group_level_vars:
                        new_group_vars[group][variable] = value 
            else:
                for variable, value in details[list(details.keys())[0]].items():
                    if variable in node_group_level_vars:
                        new_group_vars[group][variable] = value 


    # print(json.dumps(new_group_vars, indent=2))
    for group, variables in new_group_vars.items():
        for variable, value in variables.items():
            node_groups[group][variable] = value
            for variable_dict in node_groups[group]["nodes"].values():
                del(variable_dict[variable])
    return node_groups 

def parseL2LeafInfo(inventory_file):
    '''
    '''
    l2_yaml = {}
    configuration_variable_mappers = {"Platform": "platform", "Spines":"spines", "Uplink Interfaces to L3 Leafs": "uplink_interfaces",
    "MLAG Interfaces":"mlag_interfaces", "Spanning-tree Mode":"spanning_tree_mode", "Spanning-tree Priority":"spanning_tree_priority"}
    l2_leaf_info = {}
    workbook = xlrd.open_workbook(inventory_file)
    inventory_worksheet = workbook.sheet_by_name("L2 Leaf Info")
    node_groups = {}
    first_row = [] # The row where we stock the name of the column
    for col in range(inventory_worksheet.ncols):
        first_row.append( inventory_worksheet.cell_value(0,col) )
    # transform the workbook to a list of dictionaries
    for row in range(1, inventory_worksheet.nrows):
        l2_leaf_info = {}
        for col in range(inventory_worksheet.ncols):
            l2_leaf_info[first_row[col]]=inventory_worksheet.cell_value(row,col)
        hostname = l2_leaf_info["Hostname"]
        node_details = {}
        node_details["id"] = int(l2_leaf_info["ID"])
        node_details["mgmt_ip"] = l2_leaf_info["Management IP"]
        node_details["filter"] = {}
        node_details["filter"]["tenants"] = [tenant.strip() for tenant in l2_leaf_info["Tenants"].split(",") if tenant != ""]
        node_details["filter"]["tags"] = [tag.strip() for tag in l2_leaf_info["Tags"].split(",") if tag != ""]
        optional_params = {}
        optional_params["platform"] = str(l2_leaf_info["Platform"]) if l2_leaf_info["Platform"] != "" else None
        optional_params["parent_l3leafs"] = [spine.strip() for spine in l2_leaf_info["Parent Leaf Hostnames"].split(",") if spine] if l2_leaf_info["Parent Leaf Hostnames"] != "" else None
        optional_params["l3leaf_interfaces"] = [uplink_iface.strip() for uplink_iface in l2_leaf_info["L3 Leaf Interfaces"].split(",") if uplink_iface] if l2_leaf_info["L3 Leaf Interfaces"] != "" else None
        optional_params["uplink_interfaces"] = [uplink_iface.strip() for uplink_iface in l2_leaf_info["Uplink Interfaces to L3 Leafs"].split(",") if uplink_iface] if l2_leaf_info["Uplink Interfaces to L3 Leafs"] != "" else None
        optional_params["mlag_interfaces"] = [iface.strip() for iface in l2_leaf_info["MLAG Interfaces"].split(",") if iface] if l2_leaf_info["MLAG Interfaces"] != "" else None
        for k, v in optional_params.items():
            if v is not None:
                v = int(v) if type(v) == float else v
                node_details[k] = v

        if l2_leaf_info["Container Name"] not in node_groups.keys():
            node_groups[l2_leaf_info["Container Name"]] = {"nodes": {hostname: node_details}}
        else:
            node_groups[l2_leaf_info["Container Name"]]["nodes"][hostname] = node_details

    # print(yaml.dump(node_groups))
    #parse default values
    l2_defaults_worksheet = workbook.sheet_by_name("L2 Leaf Configuration Details")
    defaults = {}
    # transform the workbook to a list of dictionaries
    for row in range(1, l2_defaults_worksheet.nrows):
        k, v = l2_defaults_worksheet.cell_value(row,0), l2_defaults_worksheet.cell_value(row,1)
        if k in configuration_variable_mappers.keys() and v is not None and v != "":
            v = convertToList(v)
            v = convertToBoolIfNeeded(v)
            v = int(v) if type(v) == float else v
            defaults[configuration_variable_mappers[k]] = v

    # print(json.dumps(defaults, indent=2))
    l2_yaml["defaults"] = defaults
    l2_yaml["node_groups"] = consolidateNodeGroups(node_groups)

    return l2_yaml

def parseL3LeafInfo(inventory_file):
    '''
    '''
    l3_yaml = {}
    configuration_variable_mappers = {"Platform": "platform", "Spines":"spines", "Uplink Interfaces to Spines": "uplink_to_spine_interfaces",
    "BGP AS":"bgp_as", "MLAG Interfaces":"mlag_interfaces", "Virtual Router Mac-Address":"virtual_router_mac_address",
    "Spanning-tree Mode":"spanning_tree_mode", "Spanning-tree Priority":"spanning_tree_priority"}
    l3_leaf_info = {}
    workbook = xlrd.open_workbook(inventory_file)
    inventory_worksheet = workbook.sheet_by_name("L3 Leaf Info")
    node_groups = {}
    first_row = [] # The row where we stock the name of the column
    for col in range(inventory_worksheet.ncols):
        first_row.append( inventory_worksheet.cell_value(0,col) )
    # transform the workbook to a list of dictionaries
    for row in range(1, inventory_worksheet.nrows):
        l3_leaf_info = {}
        for col in range(inventory_worksheet.ncols):
            l3_leaf_info[first_row[col]]=inventory_worksheet.cell_value(row,col)
        hostname = l3_leaf_info["Hostname"]
        node_details = {}
        node_details["id"] = int(l3_leaf_info["ID"])
        node_details["mgmt_ip"] = l3_leaf_info["Management IP"]
        node_details["filter"] = {}
        node_details["filter"]["tenants"] = [tenant.strip() for tenant in l3_leaf_info["Tenants"].split(",") if tenant != ""]
        node_details["filter"]["tags"] = [tag.strip() for tag in l3_leaf_info["Tags"].split(",") if tag != ""]
        optional_params = {}
        optional_params["platform"] = str(l3_leaf_info["Platform"]) if l3_leaf_info["Platform"] != "" else None
        optional_params["spines"] = [spine.strip() for spine in l3_leaf_info["Spines"].split(",") if spine] if l3_leaf_info["Spines"] != "" else None
        optional_params["uplink_to_spine_interfaces"] = [uplink_iface.strip() for uplink_iface in l3_leaf_info["Uplink Interfaces to Spines"].split(",") if uplink_iface] if l3_leaf_info["Uplink Interfaces to Spines"] != "" else None
        optional_params["spine_interfaces"] = [uplink_iface.strip() for uplink_iface in l3_leaf_info["Remote Spine Interfaces"].split(",") if uplink_iface] if l3_leaf_info["Remote Spine Interfaces"] != "" else None
        optional_params["bgp_as"] = int(l3_leaf_info["BGP AS"]) if l3_leaf_info["BGP AS"] != "" else None
        optional_params["mlag_interfaces"] = [iface.strip() for iface in l3_leaf_info["MLAG Interfaces"].split(",") if iface] if l3_leaf_info["MLAG Interfaces"] != "" else None
        for k, v in optional_params.items():
            if v is not None:
                v = int(v) if type(v) == float else v
                node_details[k] = v

        if l3_leaf_info["Container Name"] not in node_groups.keys():
            node_groups[l3_leaf_info["Container Name"]] = {"nodes": {hostname: node_details}}
        else:
            node_groups[l3_leaf_info["Container Name"]]["nodes"][hostname] = node_details

    # print(yaml.dump(node_groups))
    #parse default values
    l3_defaults_worksheet = workbook.sheet_by_name("L3 Leaf Configuration Details")
    defaults = {}
    bgp_defaults = {}
    # transform the workbook to a list of dictionaries
    for row in range(1, l3_defaults_worksheet.nrows):
        k, v = l3_defaults_worksheet.cell_value(row,0), l3_defaults_worksheet.cell_value(row,1)
        if k in configuration_variable_mappers.keys() and v is not None and v != "":
            v = convertToList(v)
            v = convertToBoolIfNeeded(v)
            v = int(v) if type(v) == float else v
            defaults[configuration_variable_mappers[k]] = v

    # print(json.dumps(defaults, indent=2))
    l3_yaml["defaults"] = defaults
    l3_yaml["node_groups"] = consolidateNodeGroups(node_groups)

    return l3_yaml

def parseL3LeafBGPDefaults(inventory_file):
    #parse default values
    configuration_variable_mappers = {"BGP wait-install": "wait_install", "BGP distance setting":"distance_setting", "BGP default ipv4-unicast": "ipv4_unicast"}
    l3_leaf_info = {}
    workbook = xlrd.open_workbook(inventory_file)
    l3_defaults_worksheet = workbook.sheet_by_name("L3 Leaf Configuration Details")
    bgp_defaults = {}
    # transform the workbook to a list of dictionaries
    for row in range(1, l3_defaults_worksheet.nrows):
        k, v = l3_defaults_worksheet.cell_value(row,0), l3_defaults_worksheet.cell_value(row,1)
        if k in configuration_variable_mappers.keys() and v is not None and v != "":
            v = convertToBoolIfNeeded(v)
            bgp_defaults[configuration_variable_mappers[k]] = v
    bgp_defaults_list = []
    config_values = {
        "wait_install":
            {
                True: "update wait-install",
                False: None
            },
        "ipv4_unicast":
        {
            True: "bgp default ipv4-unicast",
            False: "no bgp default ipv4-unicast"
        }
    }
    for k, v in bgp_defaults.items():
        if k in config_values.keys():
            v = config_values[k][bool(v)]
        if v is not None:
            bgp_defaults_list.append(v)
    return bgp_defaults_list

def parseSpineInfo(inventory_file):
    '''
    '''
    spine_yaml = {"nodes": {}}

    configuration_variable_mappers = {"Platform": "platform", "BGP Peering ASN Range": "leaf_as_range", "BGP ASN":"bgp_as"}
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
        node_details = {}
        node_details["id"] = int(spine_info["ID"])
        node_details["mgmt_ip"] = spine_info["Management IP"]
        spine_yaml["nodes"][hostname] = node_details

    # print(yaml.dump(node_groups))
    #parse default values
    spine_defaults_worksheet = workbook.sheet_by_name("Spine Configuration Details")
    # transform the workbook to a list of dictionaries
    for row in range(1, spine_defaults_worksheet.nrows):
        k, v = spine_defaults_worksheet.cell_value(row,0), spine_defaults_worksheet.cell_value(row,1)
        if k in configuration_variable_mappers.keys() and v is not None and v != "":
            v = convertToBoolIfNeeded(v)
            v = int(v) if type(v) == float else v
            spine_yaml[configuration_variable_mappers[k]] = v

    # print(json.dumps(defaults, indent=2))
    return spine_yaml

def parseSpineBGPDefaults(inventory_file):
    #parse default values
    configuration_variable_mappers = {"BGP wait-for-convergence":"update_wait_for_convergence", "BGP wait-install": "wait_install", "BGP distance setting":"distance_setting", "BGP default ipv4-unicast": "ipv4_unicast"}
    workbook = xlrd.open_workbook(inventory_file)
    spine_defaults_worksheet = workbook.sheet_by_name("Spine Configuration Details")
    bgp_defaults = {}
    # transform the workbook to a list of dictionaries
    for row in range(1, spine_defaults_worksheet.nrows):
        k, v = spine_defaults_worksheet.cell_value(row,0), spine_defaults_worksheet.cell_value(row,1)
        if k in configuration_variable_mappers.keys() and v is not None and v != "":
            v = convertToBoolIfNeeded(v)
            bgp_defaults[configuration_variable_mappers[k]] = v
    bgp_defaults_list = []
    config_values = {
        "update_wait_for_convergence":
            {
                True: "update wait-for-convergence",
                False: None
            },
         "wait_install":
            {
                True: "update wait-install",
                False: None
            },
        "ipv4_unicast":
        {
            True: "bgp default ipv4-unicast",
            False: "no bgp default ipv4-unicast"
        }
    }
    for k, v in bgp_defaults.items():
        if k in config_values.keys():
            v = config_values[k][bool(v)]
        if v is not None:
            bgp_defaults_list.append(v)
    return bgp_defaults_list

def parseGeneralVariables(inventory_file):
    ''''''
    general_yaml = {}
    configuration_variable_mappers = {
        "Fabric Name": "fabric_name",
        "Underlay Network Summary": "underlay_p2p_network_summary",
        "Overlay Network Summary": "overlay_loopback_network_summary",
        "VTEP Network Summary": "vtep_loopback_network_summary",
        "MLAG IGP Peer Network Summary": "leaf_peer_l3",
        "MLAG Peer Network Summary": "mlag_peer",
        "Vxlan VLAN Aware Bundles": "vxlan_vlan_aware_bundles",
        "Point to Point Uplink MTU": "p2p_uplinks_mtu",
        "BGP IPv4 Underlay Peer Group Password": "bgp_ipv4_password",
        "BGP EVPN Overlay Peer Group Password": "bgp_evpn_password",
        "BGP MLAG IPv4 Underlay Group Password": "bgp_mlag_ipv4_password",
        "BGP BFD Multihop Interval": "bfd_interval",
        "BGP BFD Multihop Min Rx": "bfd_min_rx",
        "BGP BFD Multihop Multiplier": "bfd_multiplier"
    }
    #parse default values
    workbook = xlrd.open_workbook(inventory_file)
    general_defaults_worksheet = workbook.sheet_by_name("General Configuration Details")
    # transform the workbook to a list of dictionaries
    for row in range(1, general_defaults_worksheet.nrows):
        k, v = general_defaults_worksheet.cell_value(row,0), general_defaults_worksheet.cell_value(row,1)
        if k in configuration_variable_mappers.keys():
            v = convertToBoolIfNeeded(v)
            v = v if v != "" else None
            v = int(v) if type(v) == float else v
            general_yaml[configuration_variable_mappers[k]] = v

    general_yaml["bgp_peer_groups"] = {"IPv4_UNDERLAY_PEERS":{"password": general_yaml["bgp_ipv4_password"]},
                                        "EVPN_OVERLAY_PEERS":{"password": general_yaml["bgp_evpn_password"]},
                                        "MLAG_IPv4_UNDERLAY_PEER":{"password": general_yaml["bgp_mlag_ipv4_password"]}}
    del(general_yaml["bgp_ipv4_password"])
    del(general_yaml["bgp_evpn_password"])
    del(general_yaml["bgp_mlag_ipv4_password"])

    general_yaml["mlag_ips"] = {"leaf_peer_l3": general_yaml["leaf_peer_l3"], "mlag_peer": general_yaml["mlag_peer"]}
    del(general_yaml["leaf_peer_l3"])
    del(general_yaml["mlag_peer"])

    general_yaml["bfd_multihop"] = {"interval": general_yaml["bfd_interval"], "min_rx": general_yaml["bfd_min_rx"], "multiplier": general_yaml["bfd_multiplier"]}
    del(general_yaml["bfd_interval"])
    del(general_yaml["bfd_min_rx"])
    del(general_yaml["bfd_multiplier"])

    return general_yaml

def generateGroupVarsFabric(file_location):
    fabric_name = parseGeneralVariables(file_location)
    fabric_name["spine"] = parseSpineInfo(file_location)
    fabric_name["l3leaf"] = parseL3LeafInfo(file_location)
    fabric_name["l2leaf"] = parseL2LeafInfo(file_location)
    fabric_name["spine_bgp_defaults"] = parseSpineBGPDefaults(file_location)
    fabric_name["leaf_bgp_defaults"] = parseL3LeafBGPDefaults(file_location)
    return fabric_name
