#!/bin/bash

# Variables
zipFileName="demo_data.zip"
extractedFolder="pubmed_articles"
storageAccount="$1"
fileSystem="$2"
accountKey="$3"
baseUrl="$4"
zipUrl=${baseUrl}"Deployment/Data/demo_data.zip"


# Download the zip file
curl --output "$zipFileName" "$zipUrl"

# Extract the zip file
unzip /mnt/azscripts/azscriptinput/"$zipFileName" -d /mnt/azscripts/azscriptinput/"$extractedFolder"

az storage fs directory upload -f "$fileSystem" --account-name "$storageAccount" -s "$extractedFolder" --account-key "$accountKey" --recursive
