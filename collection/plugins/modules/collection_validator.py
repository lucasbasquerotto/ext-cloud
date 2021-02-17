#!/usr/bin/python

# (c) 2020, Lucas Basquerotto
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=wrong-import-position
# pylint: disable=import-error
# pylint: disable=broad-except

from __future__ import absolute_import, division, print_function

import os
import traceback

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.utils.display import Display

display = Display()

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

  input_arg = module.params['input'] or ''
  display.vv('collection is present - input: %s' % input_arg)

  module.exit_json(changed=False)


if __name__ == '__main__':
  main()
