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
    prepare_general_data, prepare_item_data
)


def prepare_data(raw_data):
  return prepare_general_data(
      expected_namespace='ext_s3',
      raw_data=raw_data,
      item_keys=[
          'bucket',
          'permission',
      ],
      fn_prepare_item=lambda p: prepare_item(raw_data, p),
  )


def prepare_item(raw_data, item_params):
  error_msgs = list()
  result = dict()
  state = raw_data.get('state')

  required_keys_info = dict(
      params=[
          'bucket',
      ],
      credentials=[
          'access_key',
          'secret_key',
      ],
  )

  info = prepare_item_data(
      raw_data=raw_data,
      item_params=item_params,
      default_credential_name='s3',
      required_keys_info=required_keys_info,
  )
  item_data = info.get('result')
  error_msgs += (info.get('error_msgs') or [])

  if not error_msgs:
    item_credentials = item_data.get('credentials')

    bucket = item_params.get('bucket')
    permission = item_params.get('permission') or 'private'
    mode = 'create' if (state != 'absent') else 'delete'

    endpoint = item_credentials.get('endpoint')
    access_key = item_credentials.get('access_key')
    secret_key = item_credentials.get('secret_key')

    result['bucket'] = bucket
    result['permission'] = permission
    result['mode'] = mode
    result['endpoint'] = endpoint
    result['access_key'] = access_key
    result['secret_key'] = secret_key

  return dict(result=result, error_msgs=error_msgs)
