###### Example usage
ansible-playbook -vvvv --private-key ec2.pem -u ubuntu -i ansible/inventory/test  ansible/site.yml -e girder_version=master -e cumulus_version=master
