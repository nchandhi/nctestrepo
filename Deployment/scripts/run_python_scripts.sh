#!/bin/bash
echo "started the script"

# Variables
baseUrl="$1"
keyvaultName="$2"
requirementFile="requirements.txt"
requirementFileUrl=${baseUrl}"deployment/scripts/python_script/requirements.txt"

echo "Download Started"

# Download the create_index.py file
curl --output "create_articles_index.py" ${baseUrl}"deployment/scripts/python_script/create_articles_index.py"
curl --output "create_grants_index.py" ${baseUrl}"deployment/scripts/python_script/create_grants_index.py"

# Download the requirement file
curl --output "$requirementFile" "$requirementFileUrl"

echo "Download completed"

#Replace key vault name 
sed -i "s/to-be-replaced/${keyvaultName}/g" "create_articles_index.py"
sed -i "s/to-be-replaced/${keyvaultName}/g" "create_grants_index.py"

pip install -r requirements.txt

python create_articles_index.py
python create_grants_index.py
