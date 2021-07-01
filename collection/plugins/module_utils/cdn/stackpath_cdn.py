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

import requests
import traceback

from ansible_collections.lrd.ext_cloud.plugins.module_utils.vars import (
    prepare_general_data, prepare_item_data
)

params_keys = [
    'stack_slug',
    'stack_name',
    'domain',
    'origin',
    'features',
    'configuration',
    'previous_slug',
]

credentials_keys = [
    'client_id',
    'client_secret',
    'grant_type',
]

base_url = 'https://gateway.stackpath.com'
identity_base_url = base_url + '/identity/v1'
stack_base_url = base_url + '/stack/v1'


def prepare_data(raw_data):
  return prepare_general_data(
      expected_namespace='ext_cdn',
      raw_data=raw_data,
      item_keys=params_keys,
      fn_prepare_item=lambda p: prepare_item(raw_data, p),
  )


def prepare_item(raw_data, item_params):
  error_msgs = list()
  result = dict()
  state = raw_data.get('state')

  stack_slug = item_params.get('stack_slug')
  previous_slug = item_params.get('previous_slug')

  if previous_slug and (previous_slug == stack_slug):
    error_msgs += [[
        'previous_slug: ' + previous_slug,
        'msg: previous slug is the same as the main stack slug'
    ]]

  required_keys_info = dict(
      params=params_keys,
      credentials=credentials_keys,
  )

  info = prepare_item_data(
      raw_data=raw_data,
      item_params=item_params,
      default_credential_name='cdn',
      required_keys_info=required_keys_info,
  )
  item_data = info.get('result')
  error_msgs += (info.get('error_msgs') or [])

  if not error_msgs:
    item_credentials = item_data.get('credentials')

    result['state'] = state

    for key in credentials_keys:
      result[key] = item_credentials.get(key)

    for key in params_keys:
      result[key] = item_params.get(key)

  return dict(result=result, error_msgs=error_msgs)


def manage_cdn(prepared_item):
  error_msgs = list()
  result = None

  try:
    state = prepared_item.get('state')

    identity_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.get(
        identity_base_url + '/oauth2/token',
        headers=identity_headers,
        json=dict(
            client_id=prepared_item.get('client_id'),
            client_secret=prepared_item.get('client_secret'),
            grant_type=prepared_item.get('grant_type'),
        ),
    )
    response.raise_for_status()

    create = (state == 'present')
    changed = False

    stack_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + response.get('access_token'),
    }

    stack_slug = prepared_item.get('stack_slug')
    stack_name = prepared_item.get('stack_name')

    response = requests.get(
        stack_base_url + '/stacks/' + stack_slug,
        headers=stack_headers,
    )
    response.raise_for_status()

    old_record = (response.json() or dict()).get('stack') or dict()
    old_record_id = old_record.get('id')

    if create:
      if old_record_id is None:
        response = requests.post(
            stack_base_url + '/stacks/' + stack_slug,
            headers=stack_headers,
            json=dict(
                slug=stack_slug,
                name=stack_name,
            )
        )
        response.raise_for_status()
        changed = True

      response = requests.get(
          stack_base_url + '/stacks/' + stack_slug + '/sites',
          headers=stack_headers,
      )
      response.raise_for_status()

      results = (response.json() or dict()).get('results') or []
      result_amount = len(results)

      if result_amount > 1:
        error_msgs += [[
            'stack_slug: ' (stack_slug or ''),
            'stack_name: ' (stack_name or ''),
            'msg: stackpath cdn has more than 1 site',
            'tip: use the stack slug for a single site, or specify another slug',
        ]]
      elif result_amount == 0:
        site_data = dict(
            domain=prepared_item.get('domain'),
            origin=prepared_item.get('origin'),
            features=prepared_item.get('features'),
            configuration=prepared_item.get('configuration'),
        )

        response = requests.post(
            stack_base_url + '/stacks/' + stack_slug + '/sites',
            headers=stack_headers,
            json=site_data
        )
        response.raise_for_status()
        changed = True
    else:
      if old_record:
        response = requests.delete(
            stack_base_url + '/stacks/' + stack_slug,
            headers=stack_headers,
        )
        response.raise_for_status()
        changed = True

    previous_slug = prepared_item.get('previous_slug')

    if previous_slug:
      response = requests.get(
          stack_base_url + '/stacks/' + previous_slug,
          headers=stack_headers,
      )
      response.raise_for_status()

      old_record = (response.json() or dict()).get('stack') or dict()
      old_record_id = old_record.get('id')

      if old_record_id is not None:
        response = requests.delete(
            stack_base_url + '/stacks/' + previous_slug,
            headers=stack_headers,
        )
        response.raise_for_status()
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
