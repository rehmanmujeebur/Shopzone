import boto3
from flask import current_app
from werkzeug.utils import secure_filename
import os

def upload_file_to_s3(file, folder_name):
    """
    Uploads a file to AWS S3 bucket
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
    )
    
    try:
        filename = secure_filename(file.filename)
        file_path = f"{folder_name}/{filename}"
        
        s3.upload_fileobj(
            file,
            current_app.config['S3_BUCKET_NAME'],
            file_path,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )
        
        return f"https://{current_app.config['S3_BUCKET_NAME']}.s3.amazonaws.com/{file_path}"
    except Exception as e:
        print("Something Happened: ", e)
        return None