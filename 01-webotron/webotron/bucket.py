# -*- coding: utf-8 -*-
import mimetypes
from botocore.exceptions import ClientError
from pathlib import Path
"""Classes for S3 Buckets."""

class BucketManager:
    """Manage an S3 Buckets."""
    
    def __init__(self, session):
        """Create a BucketManager object."""
        self.s3 = session.resource('s3')
        self.session = session

    
    def all_buckets(self):
        """Get an iterator for all buckets."""
        return self.s3.buckets.all()
    
    def all_objects(self, bucket_name):
        """Get an iterator for all objects in bucket."""
        return self.s3.Bucket(bucket_name).objects.all()


    def init_bucket(self, bucket_name):
        """Create Bucket"""
        s3_bucket = None
        try:
            if self.session.region_name == 'us-east-1':
                s3_bucket = self.s3.create_bucket(Bucket=bucket_name)
            else:
                s3_bucket = self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.session.region_name})
        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print("You already own this bucket.")
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise error
        
        return s3_bucket
    
    def set_policy(self, bucket):
        """Set bucket policy to public bucket"""
        policy = """
        {
            "Version":"2012-10-17",
            "Statement":[{
                "Sid":"PublicReadGetObject",
                "Effect":"Allow",
                "Principal": "*",
                "Action":["s3:GetObject"],
                "Resource":["arn:aws:s3:::%s/*"]
            }]
        }
        """ % bucket.name
        policy = policy.strip()
        pol = bucket.Policy()
        pol.put(Policy=policy)

    
    def configure_website(self, bucket):
        ws = bucket.Website()
        ws.put(WebsiteConfiguration={
            'ErrorDocument': {'Key': 'error.html'},
            'IndexDocument': {'Suffix': 'index.html'},
        })
        return

    def upload_file(self, bucket, path, key):
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            })
    

    def sync(self, pathname, bucket_name):
        """Sync the contents of all folders in path to bucket"""
        bucket = self.s3.Bucket(bucket_name)
        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.upload_file(bucket, str(p), str(p.relative_to(root)))

        handle_directory(root)