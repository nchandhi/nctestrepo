#!/bin/bash
echo "started the script"

# Variables
baseUrl="$1"
keyvaultName="$2"
requirementFile="requirements.txt"
requirementFileUrl=${baseUrl}"deployment/scripts/python_script/requirements.txt"

echo "Download Started"

# Download the create_index.py file
curl --output "create_index.py" ${baseUrl}"deployment/scripts/python_script/create_index.py"

# Download the requirement file
curl --output "$requirementFile" "$requirementFileUrl"

echo "Download completed"

#Replace key vault name 
sed -i "s/to-be-replaced/${keyvaultName}/g" "create_index.py"

pip install -r requirements.txt

python create_index.py
