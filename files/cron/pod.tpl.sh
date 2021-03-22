{% macro pod_task(arg_pod, arg_name, arg_task, arg_cron) %}

{% set var_log_dir = (arg_pod.data_dir + '/log/cron') | quote %}
{% set var_log_file = var_log_dir + '/' + (arg_name | quote) + ".`date '+\%F'`.log" %}
{% set var_run_cmd = (arg_pod.pod_dir + '/run') | quote %}

{{ arg_cron }}{{
''
}} mkdir -p {{ var_log_dir }}{{
''
}} && {{ var_run_cmd }} {{ arg_task }}{{
''
}} >> {{ var_log_file }} 2>&1

{% endmacro %}

{% set var_pods = input.pods | default([]) %}

{% if (input.pod_name | default('')) != '' %}

	{% set var_pods = [{
			'name': input.pod_name,
			'description': input.pod_description,
			'data_dir': input.data_dir,
			'pod_dir': input.pod_dir,
		}]
	%}

{% endif %}

{% for var_pod in var_pods %}

###
### pod: {{ var_pod.description }}
###

{% set var_tasks = (params.tasks is mapping)
	| ternary(params.tasks[var_pod.name] | default([]), params.tasks)
%}

{% for var_task in var_tasks %}

{% if var_task.when | default(true) | bool %}

{{ pod_task(var_pod, var_task.name, var_task.task | default(var_task.name), var_task.cron) }}

{% endif %}

{% endfor %}
{% endfor %}
