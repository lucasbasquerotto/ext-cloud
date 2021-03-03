#!/usr/bin/python

# (c) 2020, Lucas Basquerotto
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=import-error
# pylint: disable=broad-except

from __future__ import absolute_import, division, print_function
__metaclass__ = type  # pylint: disable=invalid-name

import traceback

import requests

def manage_stackscript(data):
  error_msgs = list()

  try:
    result = dict()
    data = data or dict()

    state = data.get('state') or ''
    api_token = data.get('api_token') or ''
    authorization = 'Bearer ' + api_token

    label = data.get('label') or ''
    page_size = data.get('page_size') or 100

    if not label:
      error_msgs += [['msg: label not specified for the stackscript']]

    if not state:
      error_msgs += [[
          'label: ' + str(label),
          'msg: state not specified for the stackscript',
      ]]

    if not api_token:
      error_msgs += [[
          'label: ' + str(label),
          'msg: api_token not specified for the stackscript',
      ]]

    if not error_msgs:
      api_url = 'https://api.linode.com/v4/linode/stackscripts'
      api_url_list = api_url + '?page_size=' + str(page_size)
      headers = dict(Authorization=authorization)

      response = requests.get(api_url_list, headers=headers)
      response.raise_for_status()

      old_data_list = response.json() or dict()
      old_list = old_data_list.get('data') or []
      same_label_list = [i for i in old_list if i.get('label') == label]

      changed = True
      resource_id = None

      if state != 'present':
        if same_label_list:
          resource_ids = [i.get('id') for i in same_label_list]

          for resource_id in resource_ids:
            api_url_delete = api_url + '/' + str(resource_id)
            response = requests.delete(api_url_delete, headers=headers)
            response.raise_for_status()
      else:
        data_to_send = dict(
            label=label,
            description=data.get('description'),
            images=data.get('images'),
            is_public=data.get('is_public'),
            rev_note=data.get('rev_note'),
            script=data.get('script')
        )

        data_to_send_keys = list(data_to_send.keys())

        for key in data_to_send_keys:
          if not data_to_send.get(key):
            data_to_send.pop(key, None)

        if same_label_list:
          changed = False

          same_label_item = same_label_list[0] if (len(same_label_list) > 0) else None
          resource_id = same_label_item.get('id')

          api_url_update = api_url + '/' + str(resource_id)

          response = requests.put(api_url_update, headers=headers, json=data_to_send)
          response.raise_for_status()
        else:
          response = requests.post(api_url, headers=headers, json=data_to_send)
          response.raise_for_status()

          response_data = response.json() or dict()
          resource_id = response_data.get('id') or ''

      result['changed'] = changed
      result['data'] = dict(id=resource_id)

    return dict(result=result, error_msgs=error_msgs)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to manage the stackscript',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]
    return dict(error_msgs=error_msgs)
