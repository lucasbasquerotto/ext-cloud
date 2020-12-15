#!/bin/bash
set -eou pipefail

echo "test1: {{ params.prop1 | quote }}"
echo "test2: {{ params.prop2 | quote }}"
echo "test3: {{ params.prop3 | quote }}"
echo "test4: {{ params.prop4 | quote }}"
echo "test5: {{ params.prop5 | quote }}"