# AVD Excel Loader Example Execution

The files in the **avd** folder were produced by executing the command `python main.py -f inventory.xlsx`

You will have to provide a password for the cvpadmin user as well that will serve as the `ansible_password` value used to login to CVP.  This key value pair can be found and set in the file **avd/group_vars/CVP.yml**

To execute the generated playbook, navigate into the newly produced **avd** folder and execute the command `ansible-playbook dc-fabric-deploy-cvp.yml -i inventory.yml`.