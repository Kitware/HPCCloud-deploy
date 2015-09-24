import boto.ec2
import sys
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('aws_access_key_id')
parser.add_argument('aws_secret_access_key')
parser.add_argument('region')
config = parser.parse_args()

conn = boto.ec2.connect_to_region(config.region,
                                  aws_access_key_id=config.aws_access_key_id,
                                  aws_secret_access_key=config.aws_secret_access_key)
images = conn.get_all_images(owners=['self'])

values = []
for image in images:
    values.append('"%s": "%s"' % (image.name, image.id))

print( ','.join(values))
