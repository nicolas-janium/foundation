#!/bin/sh
declare -a deploy_files=( $(git diff --name-only HEAD HEAD~1 | sed 's/main.py/deploy.sh/g') )

for i in "${deploy_files[@]}"
do
    if [[ "$i" == *"deploy.sh"* ]]; then
        bash "$i"
    fi
done