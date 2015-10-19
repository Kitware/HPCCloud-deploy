#HPC Cloud / Cumulus VM Deploy
##Linux
### Example usage

```sh
ansible-playbook -vvvv \
--private-key ec2.pem \
-u ubuntu \
-i ansible/inventory/test  \
   ansible/site.yml \
-e girder_version=master \
-e cumulus_version=master
```

### Local Installation
If [VirtualBox](https://www.virtualbox.org/wiki/Downloads), [Vagrant](https://www.vagrantup.com/) and [Ansible](http://www.ansible.com/) are installed, cumulus may also be deployed on a local virtual machine by running ```vagrant up``` from the project root directory. Otherwise each of these components may be installed on 64 bit Ubuntu 14.04 as follows:


#### Install VirtualBox 5.0
First you must add the Oracle repository to Ubuntu's package manage ```apt``` by executing the following commands:
```
wget -q http://download.virtualbox.org/virtualbox/debian/oracle_vbox.asc -O- | sudo apt-key add -

sudo sh -c 'echo "deb http://download.virtualbox.org/virtualbox/debian trusty contrib" >> /etc/apt/sources.list.d/virtualbox.list'
```

Then update and install virtualbox 5.0
```
sudo apt-get update && sudo apt-get install virtualbox-5.0

```

##### Install Ansible
Add the ansible repository to ```apt``` and install ansible
```
sudo apt-get install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt-get update && sudo apt-get install ansible
```

##### Install Vagrant 1.7.4

Ubuntu's default version of vagrant (1.4.3) is nearly 2 years old, to use this deployment script you must have a newer version of vagrant installed.  To do this download the following ```.deb``` file and install it. **important:** if you already have vagrant installed,  please do a ```sudo apt-get remove --purge vagrant``` before running the following commands:

```
wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.4_x86_64.deb -O /tmp/vagrant_1.7.4_x86_64.deb

sudo dpkg --install /tmp/vagrant_1.7.4_x86_64.deb && rm /tmp/vagrant_1.7.4_x86_64.deb
```

##OSX


- Clone this repo
- Download and install the following in order:
  - [VirtualBox 5.0](http://download.virtualbox.org/virtualbox/5.0.6/VirtualBox-5.0.6-103037-OSX.dmg)
  - [Vagrant 1.7.4](https://dl.bintray.com/mitchellh/vagrant/vagran	t_1.7.4.dmg)
  - Ansible - `sudo pip install ansible`
- Run `vagrant up` in the folder that you cloned this repository too
  - It will err if there's anything already running on the ports it needs (definitely 8888, 8080, probably 27017)


#HPC traditional cluster requirements

In order to use a cluster with HPCCloud the following requirements need to be available:

- Several [Python packages](https://github.com/Kitware/HPCCloud-deploy/blob/master/requirements-cluster.txt) are needed on the cluster. These can be install by running the following command on the clusters head node:

         sudo pip install -r requirements-cluster.txt
 The `requirements-cluster.txt` can be found at the [root of this repository](https://github.com/Kitware/HPCCloud-deploy/blob/master/requirements-cluster.txt).
- [ParaView](http://www.paraview.org) is used for running visualization tasks on the cluster so needs to be installed, the latest release can be downloaded [here](http://www.paraview.org/download/)
