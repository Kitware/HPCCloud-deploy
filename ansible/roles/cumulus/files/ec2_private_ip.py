import boto.ec2
import sys
from socket import gethostbyname
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('aws_access_key_id')
parser.add_argument('aws_secret_access_key')
parser.add_argument('region')
parser.add_argument('host')
config = parser.parse_args()

public_ip = gethostbyname(config.host)
conn = boto.ec2.connect_to_region(config.region,
                                  aws_access_key_id=config.aws_access_key_id,
                                  aws_secret_access_key=config.aws_secret_access_key)

reservations = conn.get_all_instances()
instances = [i for r in reservations for i in r.instances]

for i in instances:
    if i.ip_address == public_ip:
        print i.private_ip_address
        break
