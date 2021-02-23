#!/usr/bin/python

# (c) 2020, Lucas Basquerotto
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=import-error
# pylint: disable=broad-except

from __future__ import absolute_import, division, print_function
__metaclass__ = type  # pylint: disable=invalid-name

from ansible_collections.lrd.ext_cloud.plugins.module_utils.vars import (
    generate_values, prepare_general_data, prepare_item_data
)


def prepare_data(raw_data):
  return prepare_general_data(
      expected_namespace='ext_dns',
      raw_data=raw_data,
      item_keys=[
          'zone',
          'dns_type',
          'record',
          'ttl',
          'priority',
          'service',
          'protocol',
          'port',
          'weight',
          'credential',
          'value',
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
          'dns_type',
          'record',
      ],
      credentials=[
          'key_name',
          'key_secret',
          'key_algorithm',
          'server',
      ],
  )

  info = prepare_item_data(
      raw_data=raw_data,
      item_params=item_params,
      default_credential_name='dns',
      required_keys_info=required_keys_info,
  )
  item_data = info.get('result')
  error_msgs += (info.get('error_msgs') or [])

  if not error_msgs:
    item_credentials = item_data.get('credentials')

    raw_values = item_params.get('value')
    values_aux = generate_values(raw_values)
    dns_values = [v.get('value') for v in (values_aux or [])]

    if not dns_values:
      state = 'absent'

    result['state'] = state
    result['dns_values'] = dns_values

    result['key_name'] = item_credentials.get('key_name')
    result['key_secret'] = item_credentials.get('key_secret')
    result['key_algorithm'] = item_credentials.get('key_algorithm')
    result['server'] = item_credentials.get('server')

    result['zone'] = item_params.get('zone')
    result['dns_type'] = item_params.get('dns_type')
    result['record'] = item_params.get('record')
    result['ttl'] = item_params.get('ttl')
    result['priority'] = item_params.get('priority')
    result['service'] = item_params.get('service')
    result['protocol'] = item_params.get('protocol')
    result['port'] = item_params.get('port')
    result['weight'] = item_params.get('weight')

  return dict(result=result, error_msgs=error_msgs)
