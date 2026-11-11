#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
import requests
__metaclass__ = type

DOCUMENTATION = r'''
---
module: remove_node

short_description: Ansible module used to remove a specific node from Headscale.

version_added: "0.2.0"

description: This module takes a node id and removes that node from your Headscale tailnet.

options:
    headscale_url:
        description: This should be the address of your Headscale instance without the api path.
        required: true
        type: str 
    api_key:
        description: This is an API key generated from the Headscale instance. To do this on the Headscale server run, headscale preauthkeys create -u <user_id>
        required: true
        type: str
    node_id:
        description: This should be the node id for the node you are trying to remove from Headscale.
        required: True
        type: str

author:
    - Kiran Forrest (@kiranforrest)
'''

EXAMPLES = r'''
- name: Remove node from headscale
  thermiontech.headscale.remove_node:
    headscale_url: "https://headscale.example.com"
    api_key: "TBOYk2d.woCKtE1_NE0Ke4E7y6osPtr_2BX-NyiB"
    node_id: "56"
'''

RETURN = r'''
message:
    description: Gives useful output about the return state of the module to help troubleshoot failures or view success.
    type: str
    returned: always
    sample: 'Successfully removed node from Headscale.'
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        headscale_url=dict(type='str', required=True),
        api_key=dict(type='str', required=True),
        node_id=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    #Actual work being done by the module

    #Check to make sure that the node exists first
    api_path = f"/api/v1/node/{module.params['node_id']}"
    headers = { "Authorization": f"Bearer {module.params['api_key']}", "Content-Type": "application/json" }
    url = f"{module.params['headscale_url']}{api_path}"
    r = requests.get(url, headers=headers)

    if r.status_code == requests.codes.ok:
        #If node exists in headscale then we can try removing it
        r = requests.delete(url, headers=headers)
        if r.status_code == requests.codes.ok:
            result['changed'] = True
            result['message'] = "Successfully removed node from Headscale."
        else:
            result['changed'] = False
            result['message'] = "Unable to remove node."
    else:
        result['changed'] = False
        result['message'] = "Unable to find node with that id."
    
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()