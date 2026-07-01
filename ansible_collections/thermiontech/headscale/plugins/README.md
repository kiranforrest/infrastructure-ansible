# thermiontech.headscale.get_preAuthKey
description -  Ansible module to retrieve a preAuthKey from a Headscale instance.

Version Added - 0.1.0

## OPTIONS
### headscale_url
description - This should be the address of your headscale instance without the api path.

required - True

type - string

Default - none
### api_key
description - This is an api key generated from the headscale instance. To do this on the headscale server run ```bash headscale preauthkeys create -u <user_id>```

required - True

type - string

default - none
### user_id
description - The user that the preAuthKey should be created under.

required - False

type - integer

default - 1
### key_expiration
description - The number of minutes from preAuthKey creation that it should expire.

required - False

type - integer

default - 5
## EXAMPLES
### Create an preAuthKey
```yml
thermiontech.headscale.get_preAuthKey:
    headscale_url: "https://headscale.example.com
    api_key: "TBOYk2d.woCKtE1_NE0Ke4E7y6osPtr_2BX-NyiB"
```
### Create an preAuthKey key that has an expiration date of 10 minutes from now
```yml
thermiontech.headscale.get_preAuthKey:
    headscale_url: "https://headscale.example.com"
    api_key: "TBOYk2d.woCKtE1_NE0Ke4E7y6osPtr_2BX-NyiB"
    key_expiration: 10
```
### Fully deploy tailscale on a host by combining with the artis3n.tailscale.machine role. 
```yml
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
```
