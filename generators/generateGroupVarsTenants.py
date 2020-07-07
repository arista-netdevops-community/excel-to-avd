import xlrd, json, re, ipaddress

def generateGroupVarsTenants(inventory_file):
    workbook = xlrd.open_workbook(inventory_file)
    l3_leaf_info_worksheet = workbook.sheet_by_name("L3 Leaf Info")
    leafs = []
    first_row = [] # The row where we stock the name of the column
    for col in range(l3_leaf_info_worksheet.ncols):
        first_row.append( l3_leaf_info_worksheet.cell_value(0,col) )
    # transform the workbook to a list of dictionaries
    for row in range(1, l3_leaf_info_worksheet.nrows):
        leaf_info = {}
        for col in range(l3_leaf_info_worksheet.ncols):
            if first_row[col] in ["ID", "Hostname"]:
                leaf_info[first_row[col]]=l3_leaf_info_worksheet.cell_value(row,col)
            elif first_row[col] in ["Tags", "Tenants"]:
                leaf_info[first_row[col]]= [ x.strip() for x in l3_leaf_info_worksheet.cell_value(row,col).split(",") ]
        leafs.append(leaf_info)

    tenants_worksheet = workbook.sheet_by_name("Tenants")
    tenants = {}
    first_row = [] # The row where we stock the name of the column
    for col in range(tenants_worksheet.ncols):
        first_row.append( tenants_worksheet.cell_value(0,col) )
    # transform the workbook to a list of dictionaries
    for row in range(1, tenants_worksheet.nrows):
        tenant_info = {}
        for col in range(tenants_worksheet.ncols):
            tenant_info[first_row[col]]=tenants_worksheet.cell_value(row,col)
        tenant_name = tenant_info["Tenant"]
        if tenant_name not in tenants:
            tenants[tenant_name] = {"vrfs":{}}
        tenants[tenant_name]["mac_vrf_vni_base"] = int(tenant_info["Mac Vrf VNI Base"])
        vrf = tenant_info["Vrf"]
        if vrf not in tenants[tenant_name]["vrfs"]:
            tenants[tenant_name]["vrfs"][vrf] = {}
        tenants[tenant_name]["vrfs"][vrf]["vrf_vni"] = int(tenant_info["Vrf VNI"])
        if tenant_info["VTEP Loopback"] is not None and tenant_info["VTEP Loopback Address Range"] is not None and \
            tenant_info["VTEP Loopback"] != "" and tenant_info["VTEP Loopback Address Range"] != "":
            tenants[tenant_name]["vrfs"][vrf]["vtep_diagnostic"] = {}
            tenants[tenant_name]["vrfs"][vrf]["vtep_diagnostic"]["loopback"] = int(tenant_info["VTEP Loopback"])
            tenants[tenant_name]["vrfs"][vrf]["vtep_diagnostic"]["loopback_ip_range"] = tenant_info["VTEP Loopback Address Range"]
        if "svis" not in tenants[tenant_name]["vrfs"][vrf]:
            tenants[tenant_name]["vrfs"][vrf]["svis"] = {}
        svi = int(tenant_info["SVI"])
        tenants[tenant_name]["vrfs"][vrf]["svis"][svi] = {
            "name": tenant_info["Name"],
            "enabled": tenant_info["Enabled"],
            "tags": [ tag.strip() for tag in tenant_info["Tags"].split(",") ]
        }
        
        if tenant_info["Virtual Address Type"].strip() != "IP Address Virtual":
            subnet = ipaddress.IPv4Network(tenant_info["Virtual IP Subnet"])
            hosts = list(subnet.hosts())
            subnet_mask = subnet.prefixlen
            tenants[tenant_name]["vrfs"][vrf]["svis"][svi]["ip_virtual_router_address"] = str(hosts[0]) + "/" + str(subnet_mask)
            nodes = {}
            for leaf in leafs:
                if tenant_name in leaf["Tenants"] or "all" in leaf["Tenants"]:
                    for vlan_tag in [ tag.strip() for tag in tenant_info["Tags"].split(",") ]:
                        for leaf_tag in leaf["Tags"]:
                            if vlan_tag == leaf_tag:
                                nodes[leaf["Hostname"]] = {"ip_address": str(hosts[ int( leaf["ID"]) +1 ]) }
            tenants[tenant_name]["vrfs"][vrf]["svis"][svi]["nodes"] = nodes
            
        elif tenant_info["Virtual Address Type"].strip() != "IP Virtual Router Address":
            subnet = ipaddress.IPv4Network(tenant_info["Virtual IP Subnet"])
            hosts = list(subnet.hosts())
            subnet_mask = subnet.prefixlen
            tenants[tenant_name]["vrfs"][vrf]["svis"][svi]["ip_address_virtual"] = str(hosts[0]) + "/" + str(subnet_mask)


        if tenant_info["Vlan VNI Override"] is not None and tenant_info["Vlan VNI Override"] != "":
            tenants[tenant_name]["vrfs"][vrf]["svis"][svi]["vni_override"] = int(tenant_info["Vlan VNI Override"])

    tenant_yaml = {"tenants":tenants}
    return tenant_yaml