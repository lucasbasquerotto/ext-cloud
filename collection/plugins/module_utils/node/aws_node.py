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

from ansible_collections.lrd.ext_cloud.plugins.module_utils.vars import prepare_default_data

params_keys = [
    'availability_zone',
    'cpu_options',
    'detailed_monitoring',
    'ebs_optimized',
    'image_id',
    'instance_type',
    'name',
    'network',
    'region',
    'replicas',
    'security_groups',
    'instance_initiated_shutdown_behavior',
    'termination_protection',
    'volumes',
    'vpc_subnet_id',
    'wait_timeout',
    'vpc_name',
    'vpc_subnet_name',
]

credentials_keys = [
    'access_key',
    'secret_key',
]

contents_keys = ['user_data']


def prepare_data(raw_data):
  required_keys_info = dict(
      params=['region', 'instance_type'],
  )

  credential_name = 'node'

  data_info = dict(
      expected_namespace='ext_node',
      list_name='replicas',
      raw_data=raw_data,
      params_keys=params_keys,
      credentials_keys=credentials_keys,
      contents_keys=contents_keys,
      default_credential_name=credential_name,
      required_keys_info=required_keys_info,
      fn_finalize_item=finalize_item,
  )

  result_info = prepare_default_data(data_info)

  result = result_info.get('result')
  params = raw_data.get('params')
  all_credentials = raw_data.get('credentials') or dict()
  credentials = all_credentials.get(credential_name)
  state = raw_data.get('state')

  # if result and params and (state == 'present'):
  if result and params and state:
    vpc_name = params.get('vpc_name')
    vpc_subnet_name = params.get('vpc_subnet_name')

    if vpc_name and vpc_subnet_name:
      result['vpc'] = dict(
          name=vpc_name,
          subnet=vpc_subnet_name,
          region=params.get('region'),
          access_key=credentials.get('access_key'),
          secret_key=credentials.get('secret_key'),
      )

  return result_info


def finalize_item(item):
  if not item.get('volumes'):
    item['volumes'] = [dict(
        device_name='/dev/sda1',
        ebs=dict(delete_on_termination=False),
    )]

  return dict(result=item)
