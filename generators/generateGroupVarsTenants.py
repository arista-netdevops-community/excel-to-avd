import xlrd, json

def generateGroupVarsTenants(inventory_file):
    workbook = xlrd.open_workbook(inventory_file)
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
        if "svis" not in tenants[tenant_name]["vrfs"][vrf]:
            tenants[tenant_name]["vrfs"][vrf]["svis"] = {}
        svi = int(tenant_info["SVI"])
        tenants[tenant_name]["vrfs"][vrf]["svis"][svi] = {
            "name": tenant_info["Name"],
            "enabled": tenant_info["Enabled"],
            "ip_subnet": tenant_info["SVI Address"],
            "tags": [ tag.strip() for tag in tenant_info["Tags"].split(",") ]
        }
        if tenant_info["Vlan VNI Override"] is not None and tenant_info["Vlan VNI Override"] != "":
            tenants[tenant_name]["vrfs"][vrf]["svis"][svi]["vni_override"] = int(tenant_info["Vlan VNI Override"])

    tenant_yaml = {"tenants":tenants}
    return tenant_yaml