#!/usr/bin/python

# (c) 2020, Lucas Basquerotto
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=import-error
# pylint: disable=broad-except

from __future__ import absolute_import, division, print_function
__metaclass__ = type  # pylint: disable=invalid-name

import traceback

from ansible_collections.lrd.cloud.plugins.module_utils.lrd_utils import to_bool
from ansible_collections.lrd.ext_cloud.plugins.module_utils.vars import (
    generate_list_params, generate_values, validate_namespace
)


def prepare_data(raw_data):
  error_msgs = list()

  try:
    namespace = to_bool(raw_data.get('namespace'))
    params = raw_data.get('params')

    expected_namespace = 'ext_dns'
    info = validate_namespace(namespace, expected_namespace)
    error_msgs += (info.get('error_msgs') or list())

    keys = [
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
    ]

    list_params = generate_list_params(params, keys)

    prepared_list_params = list()

    for item_idx, item_params in enumerate(list_params):
      info = generate_prepared_item_info(raw_data, item_params)
      prepared_item_params = info.get('result')
      error_msgs_aux = info.get('error_msgs')

      for value in (error_msgs_aux or []):
        new_value = [
            'context: prepare item info',
            'list item: #' + str(item_idx + 1),
        ] + value
        error_msgs += [new_value]

      prepared_list_params += [prepared_item_params]

    result = dict(
        list=prepared_list_params,
    )

    return dict(result=result, error_msgs=error_msgs)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to prepare data',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]
    return dict(error_msgs=error_msgs)


def generate_prepared_item_info(raw_data, item_params):
  error_msgs = list()

  try:
    result = dict()

    credentials = raw_data.get('credentials') or dict()
    state = raw_data.get('state')

    raw_values = item_params.get('value')
    values = generate_values(raw_values)

    credential_name = item_params.get('credentials') or 'dns'
    item_credentials = credentials.get(credential_name)

    if credential_name not in credentials.keys():
      error_msgs += [[
          'credential name: ' + str(credential_name),
          'msg: credential name not present in the dictionary',
          'credential names found: ',
          sorted(list(credentials.keys())),
      ]]

    required_keys = [
        'zone',
        'dns_type',
        'record',
    ]

    for required_key in required_keys:
      if not item_params.get(required_key):
        error_msgs += [[
            'parameter name: ' + str(required_key),
            'msg: required property not present in the parameters',
        ]]

    required_credentials_keys = [
        'api_server',
        'api_version',
        'api_key',
        'api_secret',
    ]

    for required_key in required_credentials_keys:
      if not item_credentials.get(required_key):
        error_msgs += [[
            'credential name: ' + str(required_key),
            'msg: required property not present in the credentials',
        ]]

    result = None

    if not error_msgs:
      api_server_url = (
          item_credentials.get('api_server')
          + '/' + item_credentials.get('api_version')
          + '/domains/' + item_params.get('zone')
          + '/records/' + item_params.get('dns_type')
          + '/' + item_params.get('record')
      )
      authorization = (
          'sso-key ' + item_credentials.get('api_key')
          + ':' + item_credentials.get('api_secret')
      )

      if not values:
        state = 'absent'

      result = item_params.copy()
      result.pop('value', None)
      result['values'] = values
      result['api_server_url'] = api_server_url
      result['authorization'] = authorization
      result['state'] = state

    return dict(result=result, error_msgs=error_msgs)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to prepare item info',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]
    return dict(error_msgs=error_msgs)
