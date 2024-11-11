from aws_config import s3
import os
from datetime import datetime

class S3Helper:
    def __init__(self):
        self.bucket_name = 'pythontool'  # Default bucket
        
    def list_buckets(self):
        """Get list of all buckets"""
        try:
            return s3.list_buckets()['Buckets']
        except Exception as e:
            raise Exception(f"Failed to list buckets: {str(e)}")

    def list_bucket_contents(self, bucket_name, prefix=''):
        """List contents of a specific bucket"""
        try:
            paginator = s3.get_paginator('list_objects_v2')
            contents = []
            
            for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    contents.extend(page['Contents'])
            return contents
        except Exception as e:
            raise Exception(f"Failed to list bucket contents: {str(e)}")

    def upload_file(self, file_obj, filename, bucket_name, callback=None):
        """Upload a file to S3 with progress tracking"""
        try:
            file_obj.seek(0, 2)  # Seek to end
            file_size = file_obj.tell()  # Get size
            file_obj.seek(0)  # Reset position
            
            def s3_callback(bytes_transferred):
                if callback:
                    callback(bytes_transferred)
            
            s3.upload_fileobj(
                file_obj,
                bucket_name,
                filename,
                Callback=s3_callback
            )
            return True
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")

    def download_file(self, bucket_name, filename, destination_path, callback=None):
        """Download a file from S3 with progress tracking"""
        try:
            file_info = s3.head_object(Bucket=bucket_name, Key=filename)
            file_size = file_info['ContentLength']
            
            def s3_callback(bytes_transferred):
                if callback:
                    callback(bytes_transferred)
            
            with open(destination_path, 'wb') as file_obj:
                s3.download_fileobj(
                    bucket_name,
                    filename,
                    file_obj,
                    Callback=s3_callback
                )
            return True
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")

    def get_file_metadata(self, bucket_name, filename):
        """Get metadata for a specific file"""
        try:
            return s3.head_object(Bucket=bucket_name, Key=filename)
        except Exception as e:
            raise Exception(f"Failed to get file metadata: {str(e)}")