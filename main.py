import yaml, os, subprocess
from generators.generateInventory import generateInventory, getFabricName
from generators.generateCVPDeploymentPlaybook import generateCVPDeploymentPlaybook
from generators.generateGroupVarsAll import generateGroupVarsAll
from generators.generateGroupVarsCVP import generateGroupVarsCVP
from generators.generateGroupVarsFabric import generateGroupVarsFabric
from generators.generateGroupVarsSpines import generateGroupVarsSpines
from generators.generateGroupVarsL3Leafs import generateGroupVarsL3Leafs
from generators.generateGroupVarsL2Leafs import generateGroupVarsL2Leafs
from generators.generateGroupVarsTenants import generateGroupVarsTenants

def main():
    file_location = "PotentialAnsibleCSVTemplate.xlsx"
    fabric_name = getFabricName(file_location)
    avd = {
    "inventory": None,
    "group_vars": {
        "all": None,
        "CVP": None,
        fabric_name: None,
        "SPINES": None,
        "L3_LEAFS": None,
        "L2_LEAFS": None,
        "TENANTS":None
        },
    "dc-fabric-deploy-cvp": None,
    "dc-fabric-post-validation": None,
    "requirements": None,
    }
    avd["requirements"] = '''ansible==2.9.2
netaddr==0.7.19
Jinja2==2.10.3
requests==2.22.0
treelib==1.5.5
pytest==5.3.4
pytest-html
ward==0.34.0b0
git+https://github.com/batfish/pybatfish.git'''
    avd["inventory"] = generateInventory(file_location)
    avd["dc-fabric-deploy-cvp"] = generateCVPDeploymentPlaybook(file_location)
    avd["group_vars"]["all"] = generateGroupVarsAll(file_location)
    avd["group_vars"]["CVP"] = generateGroupVarsCVP(file_location)
    avd["group_vars"][fabric_name] = generateGroupVarsFabric(file_location)
    avd["group_vars"]["SPINES"] = generateGroupVarsSpines(file_location)
    avd["group_vars"]["L3_LEAFS"] = generateGroupVarsL3Leafs(file_location)
    avd["group_vars"]["L2_LEAFS"] = generateGroupVarsL2Leafs(file_location)
    avd["group_vars"]["TENANT_NETWORKS"] = generateGroupVarsTenants(file_location)

    #Create avd directory
    if not os.path.exists("./avd"):
        os.mkdir("./avd")

    #Install ansible collections if necessary
    if not os.path.exists("./avd/ansible_collections/arista/avd"):
        print("Installing arista.avd collection")
        process = subprocess.Popen(['ansible-galaxy', 'collection', 'install', 'arista.avd', '-p', './avd/'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
    if not os.path.exists("./avd/ansible_collections/arista/cvp"):
        print("Installing arista.cvp collection")
        process = subprocess.Popen(['ansible-galaxy', 'collection', 'install', 'arista.cvp',  '-p', './avd/'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

    #Create intended directories
    if not os.path.exists("./avd/intended/batfish"):
        os.makedirs("./avd/intended/batfish")
    if not os.path.exists("./avd/intended/configs"):
        os.makedirs("./avd/intended/configs")
    if not os.path.exists("./avd/intended/structured_configs"):
        os.makedirs("./avd/intended/structured_configs")
    if not os.path.exists("./avd/intended/structured_configs/cvp"):
        os.makedirs("./avd/intended/structured_configs/cvp")

    #Create documentation directory
    if not os.path.exists("./avd/documentation/{}".format(fabric_name)):
        os.makedirs("./avd/documentation/{}".format(fabric_name))
    if not os.path.exists("./avd/documentation/devices"):
        os.makedirs("./avd/documentation/devices")


    #Create inventory file
    with open("./avd/inventory.yml", "w") as inv:
        inv.write(yaml.dump(avd["inventory"]))

    #Create group_vars files
    if not os.path.exists("./avd/group_vars"):
        os.mkdir("./avd/group_vars")
    for k, v in avd["group_vars"].items():
        path = "./avd/group_vars/{}.yml".format(k)
        with open(path, "w") as gvfile:
            gvfile.write(yaml.dump(v))

    #!!!!Hard-code tenants for now!!!!
    # from generators.generateGroupVarsTenants import tenants_yaml
    # with open("./avd/group_vars/TENANT_NETWORKS.yml", 'w') as tenants:
    #     # tenants.write(tenants_yaml)
    #!!!Hard-code servers for now!!!
    with open("./avd/group_vars/SERVERS.yml", 'w') as tenants:
        tenants.write('port_profiles: []\nservers: []')

    #Create ansible config file
    from ansible_config import ansible_config
    with open("./avd/ansible.cfg", "w") as ans_cfg:
        ans_cfg.write(ansible_config)
    
    #Create dc-fabric-deploy-cvp.yml
    with open("./avd/dc-fabric-deploy-cvp.yml", "w") as ans_pb:
        ans_pb.write(avd["dc-fabric-deploy-cvp"])

    #Create requirements file
    with open("./avd/requirements.txt", "w") as reqs:
        reqs.write(avd["requirements"])

    #Create dc-fabric-post-validation.yml





if __name__ == "__main__":
    main()