from minio import Minio
from minio.error import S3Error
import os
import time
MINIO_ENDPOINT = "minio:9000"
USER = "user1234"
PASSWORD = "password"
BUCKET = "mybucket"
INPUT = "/app/input_files"
def connect():
    client = Minio(
        MINIO_ENDPOINT,
        access_key = USER,
        secret_key = PASSWORD,
        secure=False
    )
    return client
def create(client, BUCKET):
    if not client.bucket_exists(BUCKET):
        client.make_bucket(BUCKET)
        print(f"Bucket '{BUCKET}' created successfully.")
    else:
        print(f"Bucket '{BUCKET}' already exists.")

def upload_files(client, BUCKET, INPUT):
    if not os.path.exists(INPUT):
        print(f"Input directory '{INPUT}' does not exist.")
        return
    files = os.listdir(INPUT)
    if not files:
        print(f"No files found in '{INPUT}' to load.")
        return
    print(f"Found {len(files)} files in '{INPUT}'. loading to MinIO...")
    for file_name in files:
        file_path = os.path.join(INPUT, file_name)
        if os.path.isfile(file_path):
        # Sending files to MinIO Bucket
            client.fput_object(
            BUCKET,
            file_name, 
            file_path)
            print(f"Loaded '{file_name}' to bucket '{BUCKET}'.")
    
        else:
            print(f"'{file_name}' is not a file, skipping...")
if __name__ == "__main__":
    minio_client = connect()

    if minio_client:
        create(minio_client, BUCKET)
        upload_files(minio_client, BUCKET, INPUT)
