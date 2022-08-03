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
    'zone',
    'dns_type',
    'record',
    'proxied',
    'ttl',
    'weight',
    'credential',
    'value',
]

credentials_keys = [
    'access_key',
    'secret_key',
]


def prepare_data(raw_data):
  required_keys_info = dict(
      params=[
          'zone',
          'dns_type',
          'record',
      ],
      credentials=[],
  )

  data_info = dict(
      expected_namespace='ext_dns',
      raw_data=raw_data,
      params_keys=params_keys,
      credentials_keys=credentials_keys,
      default_credential_name='dns',
      required_keys_info=required_keys_info,
      fn_finalize_item=None,
  )

  result_aux = prepare_default_data(data_info)
  records = (result_aux.get('result') or dict()).get('list')
  error_msgs = result_aux.get('error_msgs')

  result = dict(zones=[], records=records)

  if not error_msgs:
    zones_aux = [dict(
        zone=item.get('zone'),
        access_key=item.get('access_key'),
        secret_key=item.get('secret_key'),
    ) for item in records
        if item.get('state') == 'present']

    unique_zones = set([])
    zones = []

    for item in zones_aux:
      zone_name = item.get('zone')

      if not zone_name in unique_zones:
        unique_zones.add(zone_name)
        zones += [item]

    result['zones'] = zones

  return dict(result=result, error_msgs=error_msgs)
