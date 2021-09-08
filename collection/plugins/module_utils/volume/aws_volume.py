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
    'name',
    'device_name',
    'encrypted',
    'iops',
    'kms_key_id',
    'modify_volume',
    'purge_tags',
    'region',
    'snapshot',
    'tags',
    'throughput',
    'volume_size',
    'volume_type',
    'zone',
]

credentials_keys = [
    'access_key',
    'secret_key',
]


def prepare_data(raw_data):
  required_keys_info = dict(
      params=['name', 'zone'],
      credentials=[],
  )

  data_info = dict(
      expected_namespace='ext_volume',
      raw_data=raw_data,
      params_keys=params_keys,
      credentials_keys=credentials_keys,
      default_credential_name='volume',
      required_keys_info=required_keys_info,
      fn_finalize_item=None,
  )

  return prepare_default_data(data_info)
