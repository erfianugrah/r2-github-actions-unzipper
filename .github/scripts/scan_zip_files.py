#!/usr/bin/env python3
# Script to scan R2 bucket for ZIP files

import os
import json
import boto3
from botocore.client import Config

# Configure S3 client for R2
s3 = boto3.client('s3',
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    config=Config(signature_version='v4')
)

# Set prefixes to skip
processed_prefix = "processed/"
unzipped_prefix = "unzipped/"

# Get all files
zip_files = []
print("Scanning R2 bucket for ZIP files...")
response = s3.list_objects_v2(Bucket=os.environ['R2_BUCKET_NAME'])

# Build set of already processed files
processed_files = set()
try:
    processed_response = s3.list_objects_v2(
        Bucket=os.environ['R2_BUCKET_NAME'],
        Prefix=processed_prefix
    )
    if 'Contents' in processed_response:
        for item in processed_response['Contents']:
            filename = item['Key'].replace(processed_prefix, '', 1)
            processed_files.add(filename)
except Exception as e:
    print(f"Warning: Error checking processed files: {e}")

# Find zip files
if 'Contents' in response:
    for item in response['Contents']:
        filename = item['Key']
        
        # Skip files in processed or unzipped directories
        if filename.startswith(processed_prefix) or filename.startswith(unzipped_prefix):
            continue
        
        # Skip non-zip files
        if not filename.lower().endswith('.zip'):
            continue
        
        # Skip if already processed
        base_filename = os.path.basename(filename)
        if base_filename in processed_files:
            print(f"Skipping already processed file: {filename}")
            continue
        
        # Add to list of files to process
        zip_files.append(filename)

# Output the list as JSON
print(f"Found {len(zip_files)} ZIP files to process")
output_json = json.dumps(zip_files)
with open(os.environ.get('GITHUB_OUTPUT', ''), 'a') as f:
    print(f"zip_files={output_json}", file=f)
    print(f"file_count={len(zip_files)}", file=f)