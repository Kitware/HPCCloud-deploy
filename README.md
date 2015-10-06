###### Example usage

```sh
ansible-playbook -vvvv \
--private-key ec2.pem \
-u ubuntu \
-i ansible/inventory/test  \
   ansible/site.yml \
-e girder_version=master \
-e cumulus_version=master
```

###### Local Installation 
If [Vagrant](https://www.vagrantup.com/) is installed, cumulus may also be deployed on a local virtual machine by running ```vagrant up``` from the project root directory. 

