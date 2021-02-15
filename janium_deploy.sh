#!/bin/sh
# ls -la
# git diff --name-only master master~1
declare -a deploy_files=( $(git diff --name-only master master~1 | sed 's/main.py/deploy.sh/g') )

for i in "${deploy_files[@]}"
do
    if [[ "$i" == *"deploy.sh"* ]]; then
        bash "$i"
    fi
done