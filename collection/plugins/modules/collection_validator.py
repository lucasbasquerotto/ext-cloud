#!/usr/bin/python

# (c) 2020, Lucas Basquerotto
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=wrong-import-position
# pylint: disable=import-error
# pylint: disable=broad-except

# pyright: reportUnusedImport=true
# pyright: reportUnusedVariable=true
# pyright: reportMissingImports=false

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type  # pylint: disable=invalid-name

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: lrd.ext_cloud.collection_validator
short_description: Validate a value according to a specified schema.
description:
   - Generic validator to verify if the collection is present.
version_added: "2.8"
options:
  input:
    description:
      - input argument to show when in verbose mode
    type: str
    required: true
author: "Lucas Basquerotto (@lucasbasquerotto)"
'''

# ===========================================
# Module execution.
#


def main():
  module = AnsibleModule(
      argument_spec=dict(input=dict(type='str', required=True))
  )

  module.exit_json(changed=False)


if __name__ == '__main__':
  main()
