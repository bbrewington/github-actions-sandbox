import boto3
import os
import argparse


def aws_s3_list_objects(aws_s3_bucket_name, aws_access_key_id, aws_secret_access_key, aws_file):
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

    return aws_key_list


def aws_to_gcs(aws_bucket, obj_key, gcs_bucket):
    aws_url = f'https://s3.amazonaws.com/{aws_bucket}/{obj_key}'

    if obj_key.endswith('.csv.zip'):
        key_csv = obj_key[:-4]
    elif obj_key.endswith('.zip'):
        key_csv = obj_key[:-4] + '.csv'

    gcs_bucket = 'citibike_trip_history_temp'
    gcs_url = f'gs://{gcs_bucket}/{obj_key}'
    gcs_url_csv = f'gs://{gcs_bucket}/{key_csv}'

    print(f'  Copying to GCS: {gcs_url}')
    os.system(f'curl {aws_url} | gsutil cp - {gcs_url}')
    print(f'  Unzipping')
    os.system(f'gsutil cat {gcs_url} | uncompress -cf | gsutil cp - {gcs_url_csv}')
    print(f'  Removing zip file')
    os.system(f'gsutil rm {gcs_url}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('aws_bucket')
    parser.add_argument('aws_access_key_id')
    parser.add_argument('aws_secret_access_key')
    parser.add_argument('gcs_bucket')
    parser.add_argument('--aws_file')

    args = parser.parse_args()

    aws_key_list = aws_s3_list_objects(args.aws_bucket, args.aws_access_key_id, args.aws_secret_access_key, args.aws_file)

    for obj_key in aws_key_list:
        aws_to_gcs(args.aws_bucket, obj_key, args.gcs_bucket)
