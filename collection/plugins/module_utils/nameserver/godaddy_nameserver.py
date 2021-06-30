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

import traceback

import requests

from ansible_collections.lrd.cloud.plugins.module_utils.lrd_utils import ordered
from ansible_collections.lrd.ext_cloud.plugins.module_utils.vars import (
    generate_values, prepare_general_data, prepare_item_data
)
from ansible.utils.display import Display

display = Display()


def prepare_data(raw_data):
  return prepare_general_data(
      expected_namespace='ext_nameserver',
      raw_data=raw_data,
      item_keys=[
          'zone',
          'nameservers',
      ],
      fn_prepare_item=lambda p: prepare_item(raw_data, p),
  )


def prepare_item(raw_data, item_params):
  error_msgs = list()
  result = dict()
  state = raw_data.get('state')

  required_keys_info = dict(
      params=[
          'zone',
          'nameservers',
      ],
      credentials=[
          'api_server',
          'api_version',
          'api_key',
          'api_secret',
      ],
  )

  info = prepare_item_data(
      raw_data=raw_data,
      item_params=item_params,
      default_credential_name='nameserver',
      required_keys_info=required_keys_info,
  )
  item_data = info.get('result')
  error_msgs += (info.get('error_msgs') or [])

  if not error_msgs:
    item_credentials = item_data.get('credentials')

    api_server_url = (
        item_credentials.get('api_server')
        + '/v' + item_credentials.get('api_version')
        + '/domains/' + item_params.get('zone')
    )
    authorization = (
        'sso-key ' + item_credentials.get('api_key')
        + ':' + item_credentials.get('api_secret')
    )

    raw_values = item_params.get('value')
    dns_values = generate_values(raw_values)

    if not dns_values:
      state = 'absent'

    result['api_server_url'] = api_server_url
    result['authorization'] = authorization
    result['state'] = state

    result['zone'] = item_params.get('zone')

    nameservers = item_params.get('nameservers')

    result['nameservers'] = nameservers if (
        state == 'present' and nameservers
    ) else [None]

  return dict(result=result, error_msgs=error_msgs)


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
