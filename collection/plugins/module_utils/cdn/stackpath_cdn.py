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

import traceback
import requests

from ansible_collections.lrd.ext_cloud.plugins.module_utils.utils import raise_for_status
from ansible_collections.lrd.ext_cloud.plugins.module_utils.vars import prepare_default_data

params_keys = [
    'absent',
    'when',
    'stack_slug',
    'stack_name',
    'domain',
    'origin',
    'features',
    'configuration',
    'previous_slug',
]

credentials_keys = [
    'account_id',
    'client_id',
    'client_secret',
]

# pylint: disable=invalid-name
base_url = 'https://gateway.stackpath.com'
identity_base_url = base_url + '/identity/v1'
stack_base_url = base_url + '/stack/v1'
delivery_base_url = base_url + '/delivery/v1'


def prepare_data(raw_data):
  required_keys_info = dict(
      params=['stack_slug'],
  )

  data_info = dict(
      expected_namespace='ext_cdn',
      raw_data=raw_data,
      params_keys=params_keys,
      credentials_keys=credentials_keys,
      default_credential_name='cdn',
      required_keys_info=required_keys_info,
      fn_finalize_item=finalize_item,
  )

  return prepare_default_data(data_info)


def finalize_item(item):
  error_msgs = list()

  stack_slug = item.get('stack_slug')
  previous_slug = item.get('previous_slug')

  if previous_slug and (previous_slug == stack_slug):
    error_msgs += [[
        'previous_slug: ' + previous_slug,
        'msg: previous slug is the same as the main stack slug'
    ]]

  return dict(result=item, error_msgs=error_msgs)


def manage_cdn(prepared_item):
  error_msgs = list()
  result = None

  try:
    state = prepared_item.get('state')

    identity_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.post(
        identity_base_url + '/oauth2/token',
        headers=identity_headers,
        json=dict(
            client_id=prepared_item.get('client_id'),
            client_secret=prepared_item.get('client_secret'),
            grant_type='client_credentials',
        ),
    )
    raise_for_status(response)

    create = (state == 'present')
    changed = False

    stack_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + (response.json() or dict()).get('access_token'),
    }

    stack_slug = prepared_item.get('stack_slug')
    stack_name = prepared_item.get('stack_name')

    response = requests.get(
        stack_base_url + '/stacks/' + stack_slug,
        headers=stack_headers,
    )
    raise_for_status(response, ignore_status=[404])

    old_record = response.json() or dict()
    old_record_id = old_record.get('id')

    if create:
      if old_record_id is None:
        response = requests.post(
            stack_base_url + '/stacks',
            headers=stack_headers,
            json=dict(
                account_id=prepared_item.get('account_id'),
                slug=stack_slug,
                name=stack_name,
            )
        )
        raise_for_status(response)
        changed = True

      response = requests.get(
          delivery_base_url + '/stacks/' + stack_slug + '/sites',
          headers=stack_headers,
      )
      raise_for_status(response, ignore_status=[404])

      results = (response.json() or dict()).get('results') or []
      result_amount = len(results)

      if result_amount > 1:
        error_msgs += [[
            'stack_slug: ' + (stack_slug or ''),
            'stack_name: ' + (stack_name or ''),
            'msg: stackpath cdn has more than 1 site',
            'tip: use 1 different stack slug per site',
        ]]
      elif result_amount == 0:
        site_data = dict(
            domain=prepared_item.get('domain'),
            origin=prepared_item.get('origin'),
            features=prepared_item.get('features') or ["cdn"],
            configuration=prepared_item.get('configuration'),
        )

        response = requests.post(
            delivery_base_url + '/stacks/' + stack_slug + '/sites',
            headers=stack_headers,
            json=site_data
        )
        raise_for_status(response)
        changed = True
    else:
      if old_record and (not old_record.get('status') == 'DELETE_REQUESTED'):
        response = requests.delete(
            stack_base_url + '/stacks/' + stack_slug,
            headers=stack_headers,
        )
        raise_for_status(response)
        changed = True

    previous_slug = prepared_item.get('previous_slug')

    if previous_slug:
      response = requests.get(
          stack_base_url + '/stacks/' + previous_slug,
          headers=stack_headers,
      )
      raise_for_status(response)

      old_record = (response.json() or dict()).get('stack') or dict()
      old_record_id = old_record.get('id')

      if old_record_id is not None:
        response = requests.delete(
            stack_base_url + '/stacks/' + previous_slug,
            headers=stack_headers,
        )
        raise_for_status(response)
        changed = True

    result = dict(changed=changed)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to manage stackpath cdn',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]

  return dict(result=result, error_msgs=error_msgs)
