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

from ansible_collections.lrd.ext_cloud.plugins.module_utils.vars import (
    prepare_general_data, prepare_item_data
)

params_keys = [
    'domains',
    'healthchecks',
    'backends',
    'cache_settings',
    'conditions',
    'directors',
    'gzips',
    'headers',
    'request_settings',
    'response_objects',
    'snippets',
    's3s',
    'syslogs',
    'settings',
]

credentials_keys = ['api_key']


def prepare_data(raw_data):
  return prepare_general_data(
      expected_namespace='ext_cdn',
      raw_data=raw_data,
      item_keys=params_keys,
      fn_prepare_item=lambda p: prepare_item(raw_data, p),
  )


def prepare_item(raw_data, item_params):
  error_msgs = list()
  result = dict()
  state = raw_data.get('state')

  required_keys_info = dict(
      params=params_keys,
      credentials=credentials_keys,
  )

  info = prepare_item_data(
      raw_data=raw_data,
      item_params=item_params,
      default_credential_name='cdn',
      required_keys_info=required_keys_info,
  )
  item_data = info.get('result')
  error_msgs += (info.get('error_msgs') or [])

  if not error_msgs:
    item_credentials = item_data.get('credentials')

    result['state'] = state

    for key in credentials_keys:
      result[key] = item_credentials.get(key)

    for key in params_keys:
      result[key] = item_params.get(key)

  return dict(result=result, error_msgs=error_msgs)
