ansible_config = '''[defaults]
host_key_checking = False
inventory =./inventory.yml
gathering = explicit
retry_files_enabled = False
collections_paths = ./collections:~/.ansible/collections:/usr/share/ansible/collections:../../../ansible-avd/:../../../ansible-cvp/
jinja2_extensions =  jinja2.ext.loopcontrols,jinja2.ext.do,jinja2.ext.i18n
# enable the YAML callback plugin.
stdout_callback = yaml
# enable the stdout_callback when running ad-hoc commands.
bin_ansible_callbacks = True
forks = 15
callback_whitelist = profile_roles, profile_tasks, timer

[persistent_connection]
connect_timeout = 120
command_timeout = 120'''