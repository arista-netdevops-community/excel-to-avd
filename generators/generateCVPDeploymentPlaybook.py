import xlrd, re

def getVariableFromGeneralConfiguration(inventory_file, variable):
    workbook = xlrd.open_workbook(inventory_file)
    info_worksheet = workbook.sheet_by_name("General Configuration Details")
    # transform the workbook to a list of dictionaries
    for row in range(1, info_worksheet.nrows):
        k, v = info_worksheet.cell_value(row,0), info_worksheet.cell_value(row,1)
        if k == variable:
            v = v if v != "" else None
            return v
    return None

def convertToBoolIfNeeded(variable):
    if type(variable) == str and re.match(r'(?i)(True|False)', variable.strip()):
        variable = True if re.match(r'(?i)true', variable.strip()) else False
    return variable

def generateCVPDeploymentPlaybook(inventory_file):
    fabric_name = getVariableFromGeneralConfiguration(inventory_file, "Fabric Name")
    fabric_id = getVariableFromGeneralConfiguration(inventory_file, "Fabric Identifier")
    configlet_prefix = getVariableFromGeneralConfiguration(inventory_file, "Configlet Prefix")
    validate_topo = convertToBoolIfNeeded(getVariableFromGeneralConfiguration(inventory_file, "Validate Network with Batfish"))
    cvp_deployment_playbook ='''---
- name: Build Switch configuration
  hosts: {}
  connection: local
  gather_facts: no
  tasks:
    - name: generate intented variables
      tags: [build]
      import_role:
         name: arista.avd.eos_l3ls_evpn
    - name: generate device intended config and documention
      tags: [build]
      import_role:
         name: arista.avd.eos_cli_config_gen
'''.format(fabric_name)
    if validate_topo is True:
        cvp_deployment_playbook += '''
- name: Validate DC Fabric configuration with Batfish
  hosts: localhost
  connection: local
  roles:
    - batfish.base
  vars:
    snapshot: {}-target
    network: {}
  tasks:
    - name: Pre Deployment fabric validation
      import_role:
         name: eos_pre_fabric_validation
'''.format(fabric_id, fabric_id)
    cvp_deployment_playbook += '''
- name: Configuration deployment with CVP
  hosts: CVP
  connection: local
  gather_facts: no
  tasks:
    - name: run CVP provisioning
      import_role:
         name: arista.avd.eos_config_deploy_cvp
      vars:
        container_root: '{}'
        configlets_prefix: '{}'
        device_filter: '{}'
        state: present
'''.format(fabric_name, configlet_prefix, fabric_id)
    return cvp_deployment_playbook