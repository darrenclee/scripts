import argparse
import logging
import os
import re
from datetime import datetime
from dateutil import tz
import boto3

logging.basicConfig(format='%(levelname)s:%(message)s')

#set s3_cleanup_days into lambda to run, permission through role, else user input for dev testing
def check_for_env_vars():
    for env_var in ['S3_CLEANUP_DAYS', 'AWS_PROFILE']:
        if env_var not in os.environ:
            logging.warning('%s is not set in environment variables', env_var)

def create_s3_session(profile_name=None):
    session_dict = {}
    if 'AWS_PROFILE' in os.environ:
        session_dict['profile_name'] = os.environ['AWS_PROFILE']

    if profile_name:
        session_dict['profile_name'] = profile_name

    session = boto3.Session(**session_dict)
    s3_client = session.client('s3')

    return s3_client

def get_buckets(s3_client):
    buckets = s3_client.list_buckets()
    bucket_name_list = [bucket['Name'] for bucket in buckets['Buckets']]

    return bucket_name_list

def get_days_passed_since_modified(last_modified):
    current_time = datetime.utcnow().replace(tzinfo=tz.tzutc())
    time_difference = current_time - last_modified
    days_passed = time_difference.days

    return days_passed

def get_buckets_with_objects_to_delete(s3_client, days):
    if not days:
        # days = int(365)
        logging.warning('Days passed is not set, defaulting to 365 days')
    bucket_name_list = get_buckets(s3_client)
    delete_object_dict = {}

    for bucket_name in bucket_name_list:
        try: #skip buckets with no objects
            contents = s3_client.list_objects_v2(Bucket=bucket_name)['Contents']
            folder_set = set()
            for obj in contents:
                folder_match = re.search(r'(^[\w-]+\/)[\w.-]*$', obj['Key'])
                if folder_match:
                    if bucket_name not in delete_object_dict:
                        delete_object_dict[bucket_name] = {'keys': []}
                    if get_days_passed_since_modified(obj['LastModified']) >= days:
                        delete_object_dict[bucket_name]['keys'].append({'Key': obj['Key']})
                folder_set.add(folder_match.group(1))
            delete_object_dict[bucket_name].update({'folders': folder_set})
        except:
            pass

    return delete_object_dict

def get_folders_list(folders_set):
    return [{'Key': value} for value in folders_set]

def delete_objects(s3_client, objects_dict):
    for bucket_name in objects_dict:
        s3_client.delete_objects(Bucket=bucket_name, Delete={
                'Objects': objects_dict[bucket_name]['keys']})            

        #if folder deletion happens before objects are deleted folder will be left behind, cleanup empty folder
        bucket_folder_set = get_folders_list(objects_dict[bucket_name]['folders'])
        if bucket_folder_set:
            s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': bucket_folder_set})

def s3_run(opts):
    try:
        check_for_env_vars()
        s3_client = create_s3_session(opts.profile)
        objects_to_delete = get_buckets_with_objects_to_delete(s3_client, opts.days)
        delete_objects(s3_client, objects_to_delete)
    except Exception as error:
        logging.error('Error: %s', error)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--days', help='How many days from current date to remove s3 objects', type=int, default=365)
    parser.add_argument('-p', '--profile', help='aws profile name')
    parser.description = 'S3 cleanup tool to remove objects older than a X number of days'

    return parser.parse_args()

def main():
    opts = parse_args()
    s3_run(opts)

if __name__ == "__main__":
    main()
