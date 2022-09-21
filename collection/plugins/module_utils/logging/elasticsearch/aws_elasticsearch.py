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
    'absent',
    'when',
    "name",
    "region",
    "elasticsearch_version",
    "instance_type",
    "instance_count",
    "dedicated_master",
    "zone_awareness",
    "dedicated_master_instance_type",
    "dedicated_master_instance_count",
    "ebs",
    "volume_type",
    "volume_size",
    "vpc_subnets",
    "vpc_security_groups",
    "snapshot_hour",
    "access_policies",
]

credentials_keys = [
    'access_key',
    'secret_key',
]


def prepare_data(raw_data):
  required_keys_info = dict(
      params=['name', 'region'],
      credentials=[],
  )

  data_info = dict(
      expected_namespace='ext_elasticsearch',
      raw_data=raw_data,
      params_keys=params_keys,
      credentials_keys=credentials_keys,
      default_credential_name='elasticsearch',
      required_keys_info=required_keys_info,
      fn_finalize_item=None,
  )

  result_info = prepare_default_data(data_info)

  list_items = (result_info.get('result') or {}).get('list')

  for item in list_items or []:
    item_keys = list(item.keys())

    for key in item_keys:
      if item.get(key) is None:
        item.pop(key, None)

  return result_info
