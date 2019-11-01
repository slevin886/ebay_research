import boto3
import os
from io import StringIO
from threading import Thread

s3 = boto3.resource(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)


def async_s3_write(filename, df, directory='search_results/'):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    try:
        s3.Object('geniusbidding', directory + filename).put(Body=csv_buffer.getvalue())
    except Exception as e:
        print(e)


def write_file_to_s3(filename, df):
    thr = Thread(target=async_s3_write, args=[filename, df])
    thr.start()
    return thr
