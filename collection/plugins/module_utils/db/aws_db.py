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
    'allocated_storage',
    'allow_major_version_upgrade',
    'apply_immediately',
    'auto_minor_version_upgrade',
    'availability_zone',
    'backup_retention_period',
    'ca_certificate_identifier',
    'character_set_name',
    'copy_tags_to_snapshot',
    'creation_source',
    'db_cluster_identifier',
    'db_name',
    'db_parameter_group_name',
    'db_security_groups',
    'db_snapshot_identifier',
    'db_subnet_group_name',
    'domain',
    'domain_iam_role_name',
    'enable_cloudwatch_logs_exports',
    'enable_iam_database_authentication',
    'enable_performance_insights',
    'engine',
    'engine_version',
    'final_db_snapshot_identifier',
    'force_failover',
    'force_state',
    'force_update_password',
    'instance_type',
    'iops',
    'kms_key_id',
    'license_model',
    'master_username',
    'max_allocated_storage',
    'monitoring_interval',
    'monitoring_role_arn',
    'multi_az',
    'new_db_instance_identifier',
    'option_group_name',
    'performance_insights_kms_key_id',
    'performance_insights_retention_period',
    'port',
    'preferred_backup_window',
    'preferred_maintenance_window',
    'processor_features',
    'promotion_tier',
    'publicly_accessible',
    'purge_cloudwatch_logs_exports',
    'purge_security_groups',
    'purge_tags',
    'read_replica',
    'region',
    'restore_time',
    's3_bucket_name',
    's3_ingestion_role_arn',
    's3_prefix',
    'security_token',
    'skip_final_snapshot',
    'snapshot_identifier',
    'source_db_instance_identifier',
    'source_engine',
    'source_engine_version',
    'source_region',
    'storage_encrypted',
    'storage_type',
    'tags',
    'tde_credential_arn',
    'timezone',
    'use_latest_restorable_time',
    'validate_certs',
    'vpc_security_group_ids',
    'wait',
]

credentials_keys = [
    'access_key',
    'secret_key',
    'master_user_password',
    'tde_credential_password',
]


def prepare_data(raw_data):
  required_keys_info = dict(
      params=['name'],
      credentials=[],
  )

  data_info = dict(
      expected_namespace='ext_db',
      raw_data=raw_data,
      params_keys=params_keys,
      credentials_keys=credentials_keys,
      default_credential_name='db',
      required_keys_info=required_keys_info,
      fn_finalize_item=lambda item: finalize_item(item),
  )

  return prepare_default_data(data_info)


def finalize_item(item):
  force_state = item.get('force_state')

  if force_state and (item.get('state') == 'present'):
    item.pop('force_state')
    item['state'] = force_state

  item_keys = list(item.keys())

  for key in item_keys:
    if item.get(key) is None:
      item.pop(key, None)

  return dict(result=item)
