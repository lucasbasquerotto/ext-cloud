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
    'network',
    'purge_tags',
    'region',
    'replicas',
    'security_groups',
    'instance_initiated_shutdown_behavior',
    'termination_protection',
    'volumes',
    'vpc_subnet_id',
    'wait_timeout',
]

credentials_keys = [
    'access_key',
    'secret_key',
]

contents_keys = ['user_data']

base_url = 'https://gateway.stackpath.com'
identity_base_url = base_url + '/identity/v1'
stack_base_url = base_url + '/stack/v1'


def prepare_data(raw_data):
  required_keys_info = dict(
      params=['replicas'],
      params=['image_id'],
      params=['region'],
      params=['instance_type'],
  )

  data_info = dict(
      expected_namespace='ext_node',
      list_name='replicas',
      raw_data=raw_data,
      params_keys=params_keys,
      credentials_keys=credentials_keys,
      contents_keys=contents_keys,
      default_credential_name='node',
      required_keys_info=required_keys_info,
      fn_finalize_item=lambda item: finalize_item(item),
  )

  return prepare_default_data(data_info)


def finalize_item(item):
  if not item.get('volumes'):
    item['volumes'] = [dict(
        device_name='/dev/sda1',
        ebs=dict(delete_on_termination=True),
    )]

  return dict(result=item)
