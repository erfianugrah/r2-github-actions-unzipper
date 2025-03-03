#!/usr/bin/env python3
# Script to process a single ZIP file from R2 bucket

import os
import tempfile
import zipfile
import mimetypes
import boto3
import concurrent.futures
import io
from botocore.client import Config

# Configure S3 client for R2 with increased max_pool_connections
s3_config = Config(
    signature_version='v4',
    max_pool_connections=50,
    retries={'max_attempts': 3, 'mode': 'standard'}
)

s3 = boto3.client('s3',
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    config=s3_config
)

# Set prefixes
processed_prefix = "processed/"
unzipped_prefix = "unzipped/"

# Get the file from environment
filename = os.environ['ZIP_FILE']
print(f"Processing ZIP file: {filename}")

# Function to upload a single file to R2 backup directory
def upload_to_backup(args):
    file_path, relative_path, base_folder = args
    try:
        # Get content type
        mime_type, _ = mimetypes.guess_type(file_path)
        content_type = mime_type or 'application/octet-stream'
        
        # Upload path: unzipped/base_folder/relative_path
        upload_path = f"{unzipped_prefix}{base_folder}/{relative_path}"
        
        # Upload the file
        s3.upload_file(
            file_path, 
            os.environ['R2_BUCKET_NAME'], 
            upload_path,
            ExtraArgs={'ContentType': content_type}
        )
        return True
    except Exception as e:
        print(f"Error uploading backup {relative_path}: {e}")
        return False
    
# Create temp directory
with tempfile.TemporaryDirectory() as temp_dir:
    # Download zip file
    zip_path = os.path.join(temp_dir, os.path.basename(filename))
    try:
        print(f"Downloading {filename}...")
        s3.download_file(os.environ['R2_BUCKET_NAME'], filename, zip_path)
    except Exception as e:
        print(f"Error downloading file {filename}: {str(e)}")
        exit(1)
    
    # Extract zip contents
    extract_dir = os.path.join(temp_dir, 'extracted')
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        # Extract the zip file
        file_count = 0
        upload_tasks = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            print(f"Extracting {len(file_list)} files from {filename}")
            zip_ref.extractall(extract_dir)
        
        # Base folder name for extraction (without .zip extension)
        base_folder = os.path.splitext(os.path.basename(filename))[0]
        
        # Prepare upload tasks
        for root, _, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, extract_dir)
                upload_tasks.append((file_path, relative_path, base_folder))
                file_count += 1
        
        if file_count == 0:
            print(f"Warning: ZIP file {filename} is empty!")
            exit(0)
            
        print(f"Found {file_count} files to upload")
        
        # Get the original directory where the zip file was located
        original_dir = os.path.dirname(filename)
        if original_dir and not original_dir.endswith('/'):
            original_dir += '/'
            
        # Upload files in parallel to their original location
        successful_uploads = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as upload_executor:
            upload_futures = []
            
            for file_path, relative_path, _ in upload_tasks:
                # Target path is the original directory + relative path
                target_path = f"{original_dir}{relative_path}" if original_dir else relative_path
                
                # Get content type
                mime_type, _ = mimetypes.guess_type(file_path)
                content_type = mime_type or 'application/octet-stream'
                
                # Submit upload task
                future = upload_executor.submit(
                    s3.upload_file,
                    file_path,
                    os.environ['R2_BUCKET_NAME'],
                    target_path,
                    ExtraArgs={'ContentType': content_type}
                )
                upload_futures.append((future, relative_path))
                
            # Process results as they complete
            for future, file_name in upload_futures:
                try:
                    future.result()
                    successful_uploads += 1
                except Exception as e:
                    print(f"Error uploading {file_name}: {e}")
        
        print(f"Uploaded {successful_uploads}/{file_count} extracted files to their original location")
        
        if successful_uploads == 0:
            print("Failed to upload any files - aborting")
            exit(1)
        
        # Upload files to backup location
        print(f"Creating backup copies in {unzipped_prefix}...")
        backup_uploads = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as upload_executor:
            future_to_file = {upload_executor.submit(upload_to_backup, task): task[1] for task in upload_tasks}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name = future_to_file[future]
                try:
                    if future.result():
                        backup_uploads += 1
                except Exception as e:
                    print(f"Error in backup upload: {e}")
        
        print(f"Backed up {backup_uploads}/{file_count} extracted files")
        
        # Store original zip in processed directory
        processed_key = f"{processed_prefix}{os.path.basename(filename)}"
        print(f"Storing original zip in {processed_key}")
        
        s3.copy_object(
            Bucket=os.environ['R2_BUCKET_NAME'],
            CopySource={'Bucket': os.environ['R2_BUCKET_NAME'], 'Key': filename},
            Key=processed_key
        )
        
        # Delete the original zip file
        print(f"Deleting original zip file: {filename}")
        s3.delete_object(Bucket=os.environ['R2_BUCKET_NAME'], Key=filename)
        
        print(f"Successfully processed {filename}")
        
    except zipfile.BadZipFile:
        print(f"Error: File {filename} is not a valid zip file")
        exit(1)
    except Exception as e:
        print(f"Error processing zip file {filename}: {str(e)}")
        exit(1)