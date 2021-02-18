#!/usr/bin/python

# (c) 2020, Lucas Basquerotto
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

from __future__ import absolute_import, division, print_function
__metaclass__ = type  # pylint: disable=invalid-name


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
      info =  generate_prepared_item_info(raw_data, item_params)
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
        'record_type',
        'record_name',
    ]

    for required_key in required_keys:
      if not item_params.get(required_key):
        error_msgs += [[
          'parameter name: ' + str(required_key),
          'msg: required property not present',
        ]]

    result = item_params.copy()
    result.pop('value', None)
    result['values'] = values
    result['credentials'] = item_credentials

    return dict(result=result, error_msgs=error_msgs)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to prepare item info',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]
    return dict(error_msgs=error_msgs)


def validate_namespace(namespace, expected_namespace):
  error_msgs = list()

  try:
    if not namespace:
      error_msgs += [[
        'namespace expected: ' + str(expected_namespace),
        'msg: namespace not specified',
      ]]
    elif namespace != expected_namespace:
      error_msgs += [[
          'namespace expected: ' + str(expected_namespace),
          'namespace provided: ' + str(namespace),
          'msg: namespace not specified (expected: "ext_dns")',
      ]]

    return dict(error_msgs=error_msgs)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to prepare item info',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]
    return dict(error_msgs=error_msgs)

def generate_list_params(params, keys):
  raw_list_params = params.get('list')
  raw_list_params = (
      raw_list_params
      if (params_list is not None)
      else [params]
  )

  list_params = [
      generate_param_item(keys, raw_item_params, params)
      for raw_item_params
      in (raw_list_params or [])
  ]

  return list_params

def generate_item_params(keys, raw_item_params, defaults):
  if not raw_item_params:
    return None

  defaults = defaults or dict()
  result = dict()

  for key in keys:
    param_value = get_item_param_value(key, raw_item_params, defaults)
    result[key] = param_value

  return result

def get_item_param_value(param_key, item_params, defaults):
  param_value = item_params.get(param_key)
  param_value = (
      param_value
      if (param_value is not None)
      else defaults.get(param_key)
  )
  return param_value

def generate_values(raw_values):
  if not raw_values:
    return list()

  if not isinstance(raw_values, list):
    raw_value = raw_values

    if not isinstance(raw_value, dict):
      raw_value = dict(value=raw_value)

    raw_values = [raw_value]

  return raw_values
