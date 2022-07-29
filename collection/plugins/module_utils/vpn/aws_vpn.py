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
    prepare_default_data, prepare_default_item
)

vpc_params_keys = [
    "name",
    "region",
    "cidr_block",
    "tags",
    "tenancy",
    "public_vpc",
]

vpc_credentials_keys = [
    'access_key',
    'secret_key',
]

vpc_contents_keys = []

subnets_params_keys = [
    "name",
    "cidr",
    "az",
    "map_public",
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
         else dict(result={}))

  required_keys_info = dict(
      params=['cidr'],
  )

  data_info = dict(
      expected_namespace='ext_vpn',
      list_name='subnets',
      raw_data=dict(
          namespace=raw_data.get('namespace'),
          state=raw_data.get('state'),
          params=dict(subnets=(
              (raw_data.get('params') or {}).get('vpc') or {}).get('subnets') or []
          ),
          credentials=raw_data.get('credentials'),
      ),
      params_keys=subnets_params_keys,
      credentials_keys=subnets_credentials_keys,
      contents_keys=subnets_contents_keys,
      default_credential_name='vpn',
      required_keys_info=required_keys_info,
      fn_finalize_item=finalize_subnet_item,
  )

  subnets = prepare_default_data(data_info)

  required_keys_info = dict(
      params=['name', 'region'],
  )

  data_info = dict(
      expected_namespace='ext_vpn',
      list_name='security_groups',
      raw_data=dict(
          namespace=raw_data.get('namespace'),
          state=raw_data.get('state'),
          params=dict(security_groups=(
              raw_data.get('params') or {}
          ).get('security_groups') or []),
          credentials=raw_data.get('credentials'),
      ),
      params_keys=security_groups_params_keys,
      credentials_keys=security_groups_credentials_keys,
      contents_keys=security_groups_contents_keys,
      default_credential_name='vpn',
      required_keys_info=required_keys_info,
      fn_finalize_item=None,
  )

  security_groups = prepare_default_data(data_info)

  vpc_result = vpc.get('result') or {}
  subnets_result = (subnets.get('result') or {}).get('list')
  security_groups_result = (security_groups.get('result') or {}).get('list')

  for value in (subnets_result or []):
    value['region'] = vpc_result.get('region')

  vpc_errors = vpc.get('error_msgs') or []
  subnets_errors = subnets.get('error_msgs') or []
  security_groups_errors = security_groups.get('error_msgs') or []

  error_msgs = []

  for value in (vpc_errors or []):
    new_value = ['context: vpc'] + value
    error_msgs += [new_value]

  for value in (subnets_errors or []):
    new_value = ['context: subnets'] + value
    error_msgs += [new_value]

  for value in (security_groups_errors or []):
    new_value = ['context: security groups'] + value
    error_msgs += [new_value]

  return dict(
      result=dict(
          vpc=vpc_result,
          subnets=subnets_result,
          security_groups=security_groups_result,
      ),
      error_msgs=error_msgs,
  )


def finalize_subnet_item(item):
  tags = item.get('tags') or dict()
  tags['Name'] = item.get('name')
  item['tags'] = tags
  return dict(result=item)
