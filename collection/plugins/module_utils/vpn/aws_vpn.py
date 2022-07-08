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
    "name",
    "region",
    "description",
    "vpc_id",
    "tags",
    "rules",
    "rules_egress",
]

credentials_keys = [
    'access_key',
    'secret_key',
]

contents_keys = []


def prepare_data(raw_data):
  required_keys_info = dict(
      params=['name', 'region'],
  )

  data_info = dict(
      expected_namespace='ext_vpn',
      list_name='security_groups',
      raw_data=raw_data,
      params_keys=params_keys,
      credentials_keys=credentials_keys,
      contents_keys=contents_keys,
      default_credential_name='vpn',
      required_keys_info=required_keys_info,
      fn_finalize_item=None,
  )

  return prepare_default_data(data_info)
