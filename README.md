#### Example usage

```sh
ansible-playbook -vvvv \
--private-key ec2.pem \
-u ubuntu \
-i ansible/inventory/test  \
   ansible/site.yml \
-e girder_version=master \
-e cumulus_version=master
```

##### Local Installation 
If [VirtualBox](https://www.virtualbox.org/wiki/Downloads), [Vagrant](https://www.vagrantup.com/) and [Ansible](http://www.ansible.com/) are installed, cumulus may also be deployed on a local virtual machine by running ```vagrant up``` from the project root directory. Otherwise each of these components may be installed on 64 bit Ubuntu 14.04 as follows: 


###### Install VirtualBox 5.0
First you must add the Oracle repository to Ubuntu's package manage ```apt``` by executing the following commands:
```
wget -q http://download.virtualbox.org/virtualbox/debian/oracle_vbox.asc -O- | sudo apt-key add -

sudo sh -c 'echo "deb http://download.virtualbox.org/virtualbox/debian trusty contrib" >> /etc/apt/sources.list.d/virtualbox.list'
```

Then update and install virtualbox 5.0
```
sudo apt-get update && sudo apt-get install virtualbox-5.0

```

###### Install Ansible
Add the ansible repository to ```apt``` and install ansible
```
sudo apt-get install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt-get update && sudo apt-get install ansible
```

###### Install Vagrant 1.7.4

Ubuntu's default version of vagrant (1.4.3) is nearly 2 years old, to use this deployment script you must have a newer version of vagrant installed.  To do this download the following ```.deb``` file and install it. **important:** if you already have vagrant installed,  please do a ```sudo apt-get remove --purge vagrant``` before running the following commands:

```
wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.4_x86_64.deb -O /tmp/vagrant_1.7.4_x86_64.deb

sudo dpkg --install /tmp/vagrant_1.7.4_x86_64.deb && rm /tmp/vagrant_1.7.4_x86_64.deb
```
