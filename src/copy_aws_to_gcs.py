import boto3
import os
import argparse
from google.cloud import storage
import re


def aws_s3_list_objects(aws_s3_bucket_name, aws_access_key_id, aws_secret_access_key, aws_file=None, aws_exclude_pattern=None):
    session = boto3.Session(aws_access_key_id, aws_secret_access_key)
    s3 = session.resource('s3')
    my_bucket = s3.Bucket(aws_s3_bucket_name)

    aws_key_list = []

    for obj in my_bucket.objects.all():
        if not obj.key.endswith('html'):
            aws_key_list.append(obj.key)

    if aws_file:
        assert aws_file in aws_key_list, f'{aws_file} not found in {aws_s3_bucket_name}'
        aws_key_list = [aws_file]
    
    if aws_exclude_pattern:
        aws_key_list = [key for key in aws_key_list if not bool(re.search(aws_exclude_pattern, key))]

    return aws_key_list

def gcs_list_objects(project_id, gcs_bucket, folder):
    storage_client = storage.Client(project_id)
    blobs = storage_client.list_blobs(gcs_bucket)
    if folder:
        # TODO: find a more elegant way of doing this
        return [blob.name for blob in blobs if blob.name.startswith(f'{folder}/') and blob.name != folder + '/']
    else:
        return [blob.name for blob in blobs]

def aws_to_gcs(aws_bucket, obj_key, gcs_bucket):
    aws_url = f'https://s3.amazonaws.com/{aws_bucket}/{obj_key}'

    if obj_key.endswith('.csv.zip'):
        key_csv = obj_key[:-4]
    elif obj_key.endswith('.zip'):
        key_csv = obj_key[:-4] + '.csv'

    gcs_bucket = 'citibike_trip_history_temp'
    gcs_zip_folder = f'gs://{gcs_bucket}/zipped'
    gcs_url_zip = f'{gcs_zip_folder}/{obj_key}'
    gcs_url_csv = f'gs://{gcs_bucket}/{key_csv}'

    print(f'  Copying to GCS: {gcs_url_zip}')
    os.system(f'curl {aws_url} | gsutil cp - {gcs_url_zip}')
    print(f'  Unzipping')
    os.system(f'gsutil cat {gcs_url_zip} | uncompress -cf | gsutil cp - {gcs_url_csv}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('aws_bucket')
    parser.add_argument('aws_access_key_id')
    parser.add_argument('aws_secret_access_key')
    parser.add_argument('project_id')
    parser.add_argument('gcs_bucket')
    parser.add_argument('--aws_file')
    parser.add_argument('--aws_exclude_pattern')

    args = parser.parse_args()

    # Get list of files in AWS S3 bucket
    aws_key_list = aws_s3_list_objects(args.aws_bucket, args.aws_access_key_id, args.aws_secret_access_key, \
        args.aws_file, args.aws_exclude_pattern)

    # Find files in AWS (excluding aws_exclude_pattern if specified) not in GCS zipped folder
    gcs_zipped_list = gcs_list_objects(args.project_id, args.gcs_bucket, 'zipped')
    gcs_zipped_filenames = [x.split(f'zipped/')[1] for x in gcs_zipped_list]
    files_in_aws_not_in_gcs = [f for f in aws_key_list if f not in gcs_zipped_filenames]

    # Copy to GCS {gcs_bucket}/zipped --> unzip into {gcs_bucket}
    for obj_key in files_in_aws_not_in_gcs:
        aws_to_gcs(args.aws_bucket, obj_key, args.gcs_bucket)
