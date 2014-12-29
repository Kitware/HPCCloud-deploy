import boto.ec2
import sys

region = sys.argv[1]
conn = boto.ec2.connect_to_region(region)
images = conn.get_all_images(owners=['self'])

values = []
for image in images:
    values.append('"%s": "%s"' % (image.name, image.id))

print ','.join(values)
