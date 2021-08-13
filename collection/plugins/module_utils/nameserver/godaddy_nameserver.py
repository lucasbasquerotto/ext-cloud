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

import requests
import traceback

from ansible_collections.lrd.cloud.plugins.module_utils.lrd_utils import ordered
from ansible_collections.lrd.ext_cloud.plugins.module_utils.vars import prepare_default_data
from ansible.utils.display import Display

display = Display()

params_keys = [
    'zone',
    'nameservers',
]

credentials_keys = [
    'api_server',
    'api_version',
    'api_key',
    'api_secret',
]


def prepare_data(raw_data):
  required_keys_info = dict(
      params=['zone'],
      credentials=[],
  )

  data_info = dict(
      expected_namespace='ext_nameserver',
      raw_data=raw_data,
      params_keys=params_keys,
      credentials_keys=credentials_keys,
      default_credential_name='nameserver',
      required_keys_info=required_keys_info,
      fn_finalize_item=lambda item: finalize_item(item),
  )

  return prepare_default_data(data_info)


def finalize_item(item):
  error_msgs = list()

  state = item.get('state')
  nameservers = item.get('nameservers')
  api_server_url = (
      item.get('api_server')
      + '/v' + item.get('api_version')
      + '/domains/' + item.get('zone')
  )
  authorization = (
      'sso-key ' + item.get('api_key')
      + ':' + item.get('api_secret')
  )

  item['api_server_url'] = api_server_url
  item['authorization'] = authorization
  item['nameservers'] = nameservers if (
      nameservers and (state == 'present')
  ) else [None]

  return dict(result=item, error_msgs=error_msgs)


def manage_nameserver(prepared_item):
  error_msgs = list()
  result = None

  try:
    api_server_url = prepared_item.get('api_server_url')
    authorization = prepared_item.get('authorization')
    state = prepared_item.get('state')

    create = (state == 'present')
    changed = False

    if create:
      headers = dict(
          Authorization=authorization,
          Accept='application/json'
      )

      response = requests.get(api_server_url, headers=headers)
      response.raise_for_status()

      old_records = response.json().get('nameServers') or []
      new_records = prepared_item.get('nameservers') or []

      changed = ordered(old_records) != ordered(new_records)

      if changed:
        response = requests.patch(
            api_server_url,
            headers=headers,
            json={'nameServers': new_records},
        )
        response.raise_for_status()
    else:
      # not supported by the goddaddy API
      display.vv('absent state not supported by the godaddy api')

    result = dict(changed=changed)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to manage godaddy nameservers',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]

  return dict(result=result, error_msgs=error_msgs)
