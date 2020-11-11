# AVD Excel Loader

This script allows users to create the necessary files in order to set up and run an arista.avd ansible playbook.  The script takes values input via an Excel spreadsheet and generates the required ansible inventory and variable files.

## Requirements ##

-  Python3
-  Python modules listed in requirements.txt file

## How to execute

1.  Fill out the provided spreadsheet to create your network and save.  An example is provided in the **examples** folder
2.  Execute the script by entering the command `python main.py -f <path-to-excel-file>` 
3.  A folder called **avd** should be generated.  Change directories to that folder with `cd avd`.
4.  The playbook to run the arista avd module is `dc-fabric-deploy-cvp.yaml`
5.  Make any edits to the generated playbook and other files then run the playbook by entering the command `ansible-playbook dc-fabric-deploy-cvp.yaml`

## Limitations
- There is currently no support for pre-validation or post-validation