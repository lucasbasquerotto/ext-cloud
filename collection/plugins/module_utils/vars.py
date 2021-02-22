#!/usr/bin/python

# (c) 2021, Lucas Basquerotto
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=import-error
# pylint: disable=broad-except

from __future__ import absolute_import, division, print_function
__metaclass__ = type  # pylint: disable=invalid-name

import traceback


def prepare_general_data(raw_data, expected_namespace, item_keys, fn_prepare_item):
  error_msgs = list()

  try:
    namespace = raw_data.get('namespace')
    params = raw_data.get('params')

    if expected_namespace:
      info = validate_namespace(namespace, expected_namespace)
      error_msgs += (info.get('error_msgs') or list())

    list_params = generate_list_params(params, item_keys)

    prepared_list_params = list()

    for item_idx, item_params in enumerate(list_params):
      info = fn_prepare_item(item_params)
      prepared_item_params = info.get('result')
      error_msgs_aux = info.get('error_msgs')

      for value in (error_msgs_aux or []):
        new_value = [
            'context: prepare item info',
            'list item: #' + str(item_idx + 1),
        ] + value
        error_msgs += [new_value]

      if isinstance(prepared_item_params, list):
        prepared_list_params += prepared_item_params
      else:
        prepared_list_params += [prepared_item_params]

    result = dict(
        list=prepared_list_params,
    )

    return dict(result=result, error_msgs=error_msgs)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to prepare data (general)',
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
          'msg: wrong namespace',
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
      if (raw_list_params is not None)
      else [params]
  )

  list_params = [
      generate_item_params(keys, raw_item_params, params)
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

  raw_values = (
      [raw_values]
      if not isinstance(raw_values, list)
      else raw_values
  )

  values = [
      dict(value=raw_value)
      if not isinstance(raw_value, dict)
      else raw_value
      for raw_value in raw_values
  ]

  return values


def prepare_item_data(raw_data, item_params, default_credential_name, required_keys_info):
  error_msgs = list()
  result = dict()

  try:
    credentials = raw_data.get('credentials') or dict()
    contents = raw_data.get('contents') or dict()
    input_params = raw_data.get('input') or dict()

    required_params_keys = required_keys_info.get('params') or list()
    required_credentials_keys = required_keys_info.get('credentials') or list()
    required_contents_keys = required_keys_info.get('contents') or list()
    required_input_keys = required_keys_info.get('input') or list()

    credential_name = item_params.get('credentials') or default_credential_name
    item_credentials = credentials.get(credential_name)

    if credential_name not in credentials.keys():
      error_msgs += [[
          'credential name: ' + str(credential_name),
          'msg: credential name not present in the dictionary',
          'credential names found: ',
          sorted(list(credentials.keys())),
      ]]

    for required_key in required_params_keys:
      if not item_params.get(required_key):
        error_msgs += [[
            'parameter name: ' + str(required_key),
            'msg: required property not present in the parameters',
        ]]

    for required_key in required_credentials_keys:
      if not item_credentials.get(required_key):
        error_msgs += [[
            'credential name: ' + str(required_key),
            'msg: required property not present in the credentials',
        ]]

    for required_key in required_contents_keys:
      if not contents.get(required_key):
        error_msgs += [[
            'content name: ' + str(required_key),
            'msg: required property not present in the contents',
        ]]

    for required_key in required_input_keys:
      if not input_params.get(required_key):
        error_msgs += [[
            'input name: ' + str(required_key),
            'msg: required property not present in the input',
        ]]

    result = dict(
        credentials=item_credentials,
    )

    return dict(result=result, error_msgs=error_msgs)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to prepare the item data (general)',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]
    return dict(error_msgs=error_msgs)
