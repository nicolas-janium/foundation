#!/bin/sh
# # ls -la
# git diff --name-only master master~1
# declare -a deploy_files=( $(git diff --name-only master master~1 | sed 's/main.py/deploy.sh/g') )

# # echo $deploy_files

# for i in "${deploy_files[@]}"
# do
#     if [[ "$i" == *"deploy.sh"* ]]; then
#         bash "$i"
#     fi
# done

echo "Deploying function-1..."
gcloud functions deploy hello_world --region=us-central1 --entry-point=main --runtime=python38 --trigger-http --allow-unauthenticated --source=./janium_functions/hello_world
