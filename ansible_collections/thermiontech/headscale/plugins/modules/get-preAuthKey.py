#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
import requests
from datetime import datetime
from datetime import timezone
from datetime import timedelta
__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_preAuthKey

short_description:  Ansible module to retrieve a preAuthKey from a Headscale instance. 

version_added: "0.1.0"

description: Ansible module to retrieve a preAuthKey from a Headscale instance.

options:
    headscale_url:
        description: This should be the address of your Headscale instance without the api path.
        required: true
        type: str
    api_key:
        description: This is an API key generated from the Headscale instance. To do this on the headscale server run headscale preauthkeys create -u <user_id>
        required: true
        type: str
    user_id:
        description: The user that the preAuthKey should be created under. If none is supplied then user_id = 1 is used.
        required: false
        type: int
    key_expiration:
        description: The number of minutes from preAuthKey creation that it should expire. Will default to 5 if not provided.
        required: false
        type: int 

author:
    - Kiran Forrest (@kiranforrest)
'''

EXAMPLES = r'''
- name: Create a preAuthKey.
  thermiontech.headscale.get_preAuthKey:
    headscale_url: "https://headscale.example.com
    api_key: "TBOYk2d.woCKtE1_NE0Ke4E7y6osPtr_2BX-NyiB"

- name: Create a preAuthKey that has an expiration date of 10 minutes from now.
  thermiontech.headscale.get_preAuthKey:
    headscale_url: "https://headscale.example.com"
    api_key: "TBOYk2d.woCKtE1_NE0Ke4E7y6osPtr_2BX-NyiB"
    key_expiration: 10

- name: Fully deploy tailscale on a host by combining with the artis3n.tailscale.machine role.
  - name: Deploy Tailscale
    hosts: tailscale-machines
    tasks:
    - name: Get preAuthKey
      thermiontech.headscale.get_preAuthKey:
        headscale_url: "https://headscale.example.com"
        api_key: "TBOYk2d.woCKtE1_NE0Ke4E7y6osPtr_2BX-NyiB"

    - name: Install and configure tailscale
      ansible.builtin.include_role:
        name: artis3n.tailscale.machine
      vars:
        tailscale_args: "--login-server='https://headscale.example.com'"
        tailscale_authkey: "{{ headscale_preAuthKey }}"
'''

RETURN = r'''
headscale_preAuthKey:
    description: The preAuthKey generated if the module completed successfully.
    type: str
    returned: on success
    sample: '1033bb6b2ae67bf339b1abfb2e1b70d0466ef4c284e2186b'
'''

from ansible.module_utils.basic import AnsibleModule

def get_expiration_time(expiration_minutes):
    now = datetime.now(timezone.utc)
    time_delta = timedelta(minutes=expiration_minutes)
    later = now + time_delta
    later = later.isoformat()
    later = later[:-9]
    later = later + "Z"
    return later


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        headscale_url=dict(type='str', required=True),
        api_key=dict(type='str', required=True),
        user_id=dict(type='int', required=False, default=1),
        key_expiration=dict(type='int', required=False, default=5)
    )

    result = dict(
        changed=False,
        message='',
        ansible_facts=dict(
            headscale_preAuthKey=''
        )
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    #Actual work being done by the module
    api_path = "/api/v1/preauthkey"
    headers = { "Authorization": f"Bearer {module.params['api_key']}", "Content-Type": "application/json" }
    url = f"{module.params['headscale_url']}{api_path}"
    later = get_expiration_time(module.params['key_expiration'])
    body = { "user": f"{module.params['user_id']}", "expiration": f"{later}" }
    r = requests.post(url, headers=headers, json=body)

    #Check to make sure we actually succeeded in retreiving a preAuthKey
    if r.status_code == requests.codes.ok:
        result['changed'] = True
        result['ansible_facts']['headscale_preAuthKey'] = f"{r.json()["preAuthKey"]["key"]}"
        result['message'] = f"Key id: {r.json()["preAuthKey"]["id"]} Expiration: {r.json()["preAuthKey"]["expiration"]}"
    else:
        module.fail_json(msg='Non 200 status returned from server', **result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()