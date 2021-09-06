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
    'comment',
    'aliases',
    'cache_behaviors',
    'custom_error_responses',
    'default_cache_behavior',
    'default_origin_path',
    'default_root_object',
    'e_tag',
    'enabled',
    'http_version',
    'ipv6_enabled',
    'logging',
    'origins',
    'price_class',
    'purge_aliases',
    'purge_cache_behaviors',
    'purge_custom_error_responses',
    'purge_origins',
    'purge_tags',
    'region',
    'restrictions',
    'tags',
    'validate_certs',
    'wait',
    'wait_timeout',
    'web_acl_id',
]

credentials_keys = [
    'access_key',
    'secret_key',
]


def prepare_data(raw_data):
  required_keys_info = dict(
      params=['name'],
      credentials=[],
  )

  data_info = dict(
      expected_namespace='ext_cdn',
      raw_data=raw_data,
      params_keys=params_keys,
      credentials_keys=credentials_keys,
      default_credential_name='cdn',
      required_keys_info=required_keys_info,
      fn_finalize_item=lambda item: finalize_item(item),
  )

  return prepare_default_data(data_info)


def finalize_item(item):
  item_keys = list(item.keys())

  for key in item_keys:
    if item.get(key) is None:
      item.pop(key, None)

  return dict(result=item)
