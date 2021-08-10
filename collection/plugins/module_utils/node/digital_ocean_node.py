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

from ansible_collections.lrd.cloud.plugins.module_utils.lrd_utils import to_bool

import traceback


def prepare_data(raw_data):
  error_msgs = list()

  try:
    params = raw_data.get('params', {})

    replicas = params.get('replicas', [])
    replica_volumes = params.get('replica_volumes', [])
    volumes_to_attach = params.get('volumes_to_attach', [])

    droplets = []

    volumes_to_create = list()
    volumes_to_destroy = list()

    for replica_idx, replica in enumerate(replicas):
      info = prepare_droplet(
          replica,
          raw_data=raw_data
      )
      droplet = info.get('result')
      error_msgs_aux = info.get('error_msgs')
      volumes_names = volumes_to_attach

      for value in (error_msgs_aux or []):
        new_value = [
            'context: prepare droplet',
            'list item: #' + str(replica_idx + 1),
        ] + value
        error_msgs += [new_value]

      if not error_msgs_aux:
        for volume_idx, volume in enumerate(replica_volumes):
          info = prepare_volume(
              volume,
              replica=replica,
              raw_data=raw_data
          )
          droplet_volume = info.get('result')
          error_msgs_aux = info.get('error_msgs')

          for value in (error_msgs_aux or []):
            new_value = [
                'context: prepare droplet volume',
                'list item: #' + str(volume_idx + 1),
            ] + value
            error_msgs += [new_value]

          if not error_msgs_aux:
            if not droplet_volume.get('skip'):
              if droplet_volume.get('state') == 'absent':
                volumes_to_destroy += [droplet_volume]
              else:
                volumes_to_create += [droplet_volume]

            volumes_names += [droplet_volume.get('name')]

        droplet['volumes'] = volumes_names

        droplets += [droplet]

    result = dict(
        volumes_to_create=volumes_to_create,
        droplets=droplets,
        volumes_to_destroy=volumes_to_destroy,
    )

    return dict(result=result, error_msgs=error_msgs)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to prepare data (digital ocean node)',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]
    return dict(error_msgs=error_msgs)


def prepare_droplet(replica, raw_data):
  error_msgs = list()

  try:
    state = raw_data.get('state')
    params = raw_data.get('params', {})
    credentials = raw_data.get('credentials', {})
    contents = raw_data.get('contents', {})

    node_credentials = credentials.get('node')

    result = dict(
        name=replica.get('name'),
        state=('absent' if replica.get('absent') else state),
        oauth_token=node_credentials.get('api_token'),
        region_id=params.get('region_id'),
        size_id=params.get('size_id'),
        image_id=params.get('image_id'),
        wait_timeout=params.get('wait_timeout') or 300,
        monitoring=params.get('monitoring'),
        resize_disk=params.get('resize_disk'),
        ipv6=params.get('ipv6'),
        user_data=contents.get('user_data'),
    )

    return dict(result=result, error_msgs=error_msgs)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to prepare droplet',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]
    return dict(error_msgs=error_msgs)


def prepare_volume(volume, replica, raw_data):
  error_msgs = list()

  try:
    state = raw_data.get('state')
    params = raw_data.get('params', {})
    credentials = raw_data.get('credentials', {})

    node_credentials = credentials.get('node')

    volume_name = (
        volume.get('prefix', '') +
        replica.get('name') +
        volume.get('suffix', '')
    )
    skip = (
        (not to_bool(volume.get('when', True)))
        or
        (
            (state != 'present') and (not volume.get('can_destroy'))
        )
    )

    result = dict(
        name=volume_name,
        state=(state if volume.get('can_destroy') else 'present'),
        skip=skip,
        oauth_token=node_credentials.get('api_token'),
        region=params.get('region_id'),
        block_size=volume.get('block_size'),
    )

    return dict(result=result, error_msgs=error_msgs)
  except Exception as error:
    error_msgs += [[
        'msg: error when trying to prepare volume',
        'error type: ' + str(type(error)),
        'error details: ',
        traceback.format_exc().split('\n'),
    ]]
    return dict(error_msgs=error_msgs)
