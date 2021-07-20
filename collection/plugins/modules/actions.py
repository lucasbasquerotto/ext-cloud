#!/usr/bin/python

# (c) 2020, Lucas Basquerotto
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=import-error
# pylint: disable=broad-except

# pyright: reportUnusedImport=true
# pyright: reportUnusedVariable=true
# pyright: reportMissingImports=false

from __future__ import absolute_import, division, print_function
__metaclass__ = type  # pylint: disable=invalid-name

from ansible_collections.lrd.cloud.plugins.module_utils.lrd_utils import error_text
from ansible_collections.lrd.ext_cloud.plugins.module_utils.cdn.stackpath_cdn import (
    manage_cdn as stackpath_manage_cdn
)
from ansible_collections.lrd.ext_cloud.plugins.module_utils.dns.godaddy_dns import (
    manage_dns as godaddy_manage_dns
)
from ansible_collections.lrd.ext_cloud.plugins.module_utils.nameserver.godaddy_nameserver import (
    manage_nameserver as godaddy_manage_nameserver
)
from ansible_collections.lrd.ext_cloud.plugins.module_utils.node.linode_node import (
    manage_stackscript as linode_manage_stackscript
)

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule

# ===========================================
# Module execution.
#


def main():
  module = AnsibleModule(
      argument_spec=dict(
          identifier=dict(type='str', required=True),
          data=dict(type='raw', required=True),
      )
  )

  identifier = module.params['identifier']
  data = module.params['data']

  info = None
  result_data = None
  changed = False
  error_msgs = list()

  if not identifier:
    error_msgs += [['msg: identifier not defined']]
  elif identifier == 'godaddy_nameserver':
    info = godaddy_manage_nameserver(prepared_item=data)
  elif identifier == 'godaddy_dns':
    info = godaddy_manage_dns(prepared_item=data)
  elif identifier == 'stackpath_cdn':
    info = stackpath_manage_cdn(prepared_item=data)
  elif identifier == 'linode_stackscript':
    info = linode_manage_stackscript(data=data)
  else:
    error_msgs += [['msg: invalid identifier']]

  if info:
    result = info.get('result')
    error_msgs += (info.get('error_msgs') or list())

  if error_msgs:
    context = 'actions module (identifier: ' + str(identifier or '') + ')'
    module.fail_json(msg=to_text(error_text(error_msgs, context)))

  changed = result.get('changed')
  result_data = result.get('data')

  module.exit_json(changed=changed, data=result_data)


if __name__ == '__main__':
  main()
