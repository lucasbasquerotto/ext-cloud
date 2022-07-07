#!/usr/bin/python

# (c) 2021, Lucas Basquerotto
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


def prepare_default_data(data_info):
  expected_namespace = data_info.get('expected_namespace')
  raw_data = data_info.get('raw_data')
  params_keys = data_info.get('params_keys')
  list_name = data_info.get('list_name')

  return prepare_general_data(
      expected_namespace=expected_namespace,
      raw_data=raw_data,
      item_keys=params_keys,
      list_name=list_name,
      fn_prepare_item=lambda p: prepare_default_item(
          data_info=data_info,
          item_params=p,
      ),
  )


def prepare_default_item(data_info, item_params):
  error_msgs = list()
  result = dict()

  raw_data = data_info.get('raw_data', {})
  params_keys = data_info.get('params_keys', {})
  credentials_keys = data_info.get('credentials_keys', {})
  contents_keys = data_info.get('contents_keys', {})
  default_credential_name = data_info.get('default_credential_name')
  required_keys_info = data_info.get('required_keys_info', {})
  fn_finalize_item = data_info.get('fn_finalize_item')

  state = raw_data.get('state')

  info = prepare_item_data(
      raw_data=raw_data,
      item_params=item_params,
      default_credential_name=default_credential_name,
      required_keys_info=required_keys_info,
  )
  item_data = info.get('result')
  error_msgs += (info.get('error_msgs') or [])

  if not error_msgs:
    item_contents = item_data.get('contents', {})
    item_credentials = item_data.get('credentials', {})

    result['state'] = state

    for key in contents_keys:
      result[key] = item_contents.get(key)

    for key in credentials_keys:
      result[key] = item_credentials.get(key)

    for key in params_keys:
      result[key] = item_params.get(key)

    if result.get('absent'):
      result['state'] = 'absent'
      result.pop('absent', None)

    if fn_finalize_item:
      info = fn_finalize_item(result)
      result = info.get('result')
      error_msgs = info.get('error_msgs') or []

  return dict(result=result, error_msgs=error_msgs)


def prepare_general_data(
        raw_data,
        expected_namespace,
        item_keys,
        list_name=None,
        fn_prepare_item=None):
  error_msgs = list()

  try:
    namespace = raw_data.get('namespace')
    params = raw_data.get('params')
    list_name = list_name or 'list'

    if expected_namespace:
      info = validate_namespace(namespace, expected_namespace)
      error_msgs += (info.get('error_msgs') or list())

    list_params = generate_list_params(
        params=params,
        keys=item_keys,
        list_name=list_name
    )

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


def generate_list_params(params, keys, list_name):
  raw_list_params = params.get(list_name)

  raw_list_params = (
      raw_list_params
      if (raw_list_params is not None)
      else [params]
  )

  list_params_aux = [
      generate_item_params(keys, raw_item_params, params)
      for raw_item_params
      in (raw_list_params or [])
  ]

  list_params = [
      item
      for item in list_params_aux
      if (item.get('when') if (item.get('when') is not None) else True)
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
