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

from ansible_collections.lrd.ext_cloud.plugins.module_utils.vars import prepare_default_data, prepare_default_item

vpc_params_keys = [
    "name",
    "region",
    "cidr_block",
    "tags",
    "tenancy",
]

vpc_credentials_keys = [
    'access_key',
    'secret_key',
]

vpc_contents_keys = []

subnets_params_keys = [
    "name",
    "region",
    "cidr",
    "tags",
]

subnets_credentials_keys = [
    'access_key',
    'secret_key',
]

subnets_contents_keys = []

security_groups_params_keys = [
    "name",
    "region",
    "description",
    "vpc_id",
    "tags",
    "rules",
    "rules_egress",
]

security_groups_credentials_keys = [
    'access_key',
    'secret_key',
]

security_groups_contents_keys = []


def prepare_data(raw_data):
  required_keys_info = dict(
      params=['name', 'region', 'cidr_block'],
  )

  data_info = dict(
      expected_namespace='ext_vpn',
      raw_data=raw_data,
      params_keys=vpc_params_keys,
      credentials_keys=vpc_credentials_keys,
      contents_keys=vpc_contents_keys,
      default_credential_name='vpn',
      required_keys_info=required_keys_info,
      fn_finalize_item=None,
  )

  item_params = raw_data.get('params', {}).get('vpc')

  vpc = (prepare_default_item(data_info, item_params)
         if item_params is not None
         else None)

  required_keys_info = dict(
      params=['name', 'region', 'cidr'],
  )

  data_info = dict(
      expected_namespace='ext_vpn',
      list_name='subnets',
      raw_data=raw_data,
      params_keys=subnets_params_keys,
      credentials_keys=subnets_credentials_keys,
      contents_keys=subnets_contents_keys,
      default_credential_name='vpn',
      required_keys_info=required_keys_info,
      fn_finalize_item=None,
  )

  subnets = prepare_default_data(data_info)

  required_keys_info = dict(
      params=['name', 'region'],
  )

  data_info = dict(
      expected_namespace='ext_vpn',
      list_name='security_groups',
      raw_data=raw_data,
      params_keys=security_groups_params_keys,
      credentials_keys=security_groups_credentials_keys,
      contents_keys=security_groups_contents_keys,
      default_credential_name='vpn',
      required_keys_info=required_keys_info,
      fn_finalize_item=None,
  )

  security_groups = prepare_default_data(data_info)

  required_keys_info = dict(
      params=['name', 'region'],
  )

  data_info = dict(
      expected_namespace='ext_vpn',
      list_name='security_groups',
      raw_data=raw_data,
      params_keys=security_groups_params_keys,
      credentials_keys=security_groups_credentials_keys,
      contents_keys=security_groups_contents_keys,
      default_credential_name='vpn',
      required_keys_info=required_keys_info,
      fn_finalize_item=None,
  )

  security_groups = prepare_default_data(data_info)

  return dict(
      result=dict(
          vpc=vpc.get('result') or {},
          subnets=(subnets.get('result') or {}).get('list'),
          security_groups=(security_groups.get('result') or {}).get('list'),
      ),
      error_msgs=(security_groups.get('error_msgs') or []))
