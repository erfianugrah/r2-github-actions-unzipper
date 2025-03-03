#!/usr/bin/env python3
# Script to clean up processed files and their backups

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

# Get list of processed zip files from this run
zip_files = json.loads(os.environ['ZIP_FILES'])
print(f"Processing cleanup for {len(zip_files)} zip files")

# Set prefixes
processed_prefix = "processed/"
unzipped_prefix = "unzipped/"

# Build list of objects to delete
objects_to_delete = []

# For each zip file that was processed in this run
for zip_file in zip_files:
    zip_basename = os.path.basename(zip_file)
    base_folder = os.path.splitext(zip_basename)[0]
    
    # Add the processed zip file
    processed_key = f"{processed_prefix}{zip_basename}"
    objects_to_delete.append(processed_key)
    print(f"Will delete processed file: {processed_key}")
    
    # Find and add all files in the unzipped backup directory for this zip
    backup_prefix = f"{unzipped_prefix}{base_folder}/"
    
    continuation_token = None
    backup_count = 0
    
    while True:
        list_args = {
            'Bucket': os.environ['R2_BUCKET_NAME'],
            'Prefix': backup_prefix
        }
        
        if continuation_token:
            list_args['ContinuationToken'] = continuation_token
    
        response = s3.list_objects_v2(**list_args)
        
        if 'Contents' in response:
            for item in response['Contents']:
                objects_to_delete.append(item['Key'])
                backup_count += 1
        
        if not response.get('IsTruncated'):
            break
            
        continuation_token = response.get('NextContinuationToken')
    
    print(f"Will delete {backup_count} backup files for {base_folder}")

# Delete objects in batches of 1000 (S3 limit)
total_deleted = 0
batch_size = 1000

for i in range(0, len(objects_to_delete), batch_size):
    batch = objects_to_delete[i:i+batch_size]
    
    if not batch:
        continue
        
    delete_response = s3.delete_objects(
        Bucket=os.environ['R2_BUCKET_NAME'],
        Delete={'Objects': [{'Key': key} for key in batch]}
    )
    
    batch_deleted = len(batch)
    total_deleted += batch_deleted
    print(f"Deleted batch of {batch_deleted} objects")
    
    if 'Errors' in delete_response and delete_response['Errors']:
        for error in delete_response['Errors']:
            print(f"Error deleting {error['Key']}: {error['Message']}")
            total_deleted -= 1

print(f"Total deleted objects: {total_deleted}")
print("Cleanup completed successfully")