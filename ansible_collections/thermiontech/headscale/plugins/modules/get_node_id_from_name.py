#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
import requests
__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_node_id_from_name

short_description: Ansible module to retrieve a headscale node id based on the node name.


version_added: "0.2.0"

description: This module retrieves a node id from a headscale instance based on the node name given. Most of the time node names in headscale will just be the hostname at the time of login.

options:
    headscale_url:
        description: This should be the address of your Headscale instance without the api path.
        required: true
        type: str
    api_key:
        description: This is an API key generated from the Headscale instance. To do this on the Headscale server run, headscale preauthkeys create -u <user_id>
        required: true
        type: str
    name:
        description: This should be the node name you are trying to get a node id for.
        required: True
        type: str

author:
    - Kiran Forrest (@kiranforrest)
'''

EXAMPLES = r'''
- name: Get node id from Headscale instance
  thermiontech.headscale.get_node_id_from_name:
    headscale_url: "https://headscale.example.com"
    api_key: "TBOYk2d.woCKtE1_NE0Ke4E7y6osPtr_2BX-NyiB"
    name: "prod-prm-vm-ubusrv-caddy-01"
'''


RETURN = r'''
headscale_node_id:
    description: The node id associated with the given input node name.
    type: str
    returned: on success
    sample: '56'
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        headscale_url=dict(type='str', required=True),
        api_key=dict(type='str', required=True),
        name=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
        ansible_facts=dict(
            headscale_node_id=''
        )
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    #Actual work being done by the module
    api_path = "/api/v1/node"
    headers = { "Authorization": f"Bearer {module.params['api_key']}", "Content-Type": "application/json" }
    url = f"{module.params['headscale_url']}{api_path}"
    r = requests.get(url, headers=headers)

    #Check to make sure we actually succeeded in getting a list of nodes
    if r.status_code == requests.codes.ok:
        target_node = next((node for node in r.json()["nodes"] if node.get("name") == module.params['name']), None)
        #Check to make sure that our target_node name exists
        if target_node != None:
            target_id = target_node.get("id")
            result['ansible_facts']['headscale_node_id'] = target_id
            result['message'] = f"Node id: {target_id}"
        else:
            module.fail_json(msg='No node with such name in tailnet', **result)
    else:
        module.fail_json(msg='Non 200 status returned from server', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()