# HPCCloud - prebuilt

This directory provide various Vagrant file based on already built VMs. 
This allow us to skip the provisioning steps and be only dependent of your network speed.

## hpccloud-server

This directory contains a Vagrant file which will start a VM with the Web infrastructure of HPCCloud.
This will allow you to run ParaView, PyFr and OpenFOAM examples on hardware supporting those runtimes.
But for that you will have to register Clusters and or create AWS profiles.

The following set of commands explain how to start the VM and connect to it.

```sh
$ cd prebuilt-VMs/hpccloud-server
$ vagrant up
```

Then you should be able to connect to `http://localhost:8888` and create your user. Once you've created your user, you should edit your preferences to register cluster or define AWS profiles.

## compute-node

This directory contains a Vagrant file which will start a VM with the runtime infrastructure for ParaView/PyFr/OpenFOAM.
This VM can be seen as a `Cluster` and be registered as such in a running `hpccloud-server`.

To do so you will have to start it with the following command lines:

```sh
$ cd prebuilt-VMs/compute-node
$ vagrant up
```

And register it to your HPCCloud server like described below:

- Go to your HPCCloud server (http://localhost:8888)
- Preferences
  - Cluster [+]
    - Use "ComputeNode" preset

The configuration should be as follow:
  - Name: ComputeVM
  - Hostname: 192.168.100.100
  - Username: demo
  - Output directory: /home/demo/
  - Scheduler: Sun Grid Engine
  - Number of slots: 1
  - GPUs/Node: 0
  - Parallel Environment: 
  - Max runtime: 0 / 0 / 0
  - Default queue: 
  - OpenFoam
    - OpenFoam enabled: true
  - PyFr
    - ParaView Directory: /opt/paraview
    - Cuda enabled: OFF
    - OpenCL configurations: Empty
    - OpenMP configurations:
      - Default: 
        - Profile name: Default
        - BLAS library: /usr/lib/libblas/libblas.so

Once you save the cluster, a key pair will be generated and a command line will be suggested for adding the public key to that host.
But since you may not have a password access to that VM, you may need to add that key in a different manner.

Below is an example on how to do so while copying the key from that suggested command line.

```sh
# Those should be executed after the one listed above
$ vagrant ssh
$ sudo -iu demo
$ mkdir -p ~/.ssh 
$ echo "ssh-rsa [...] cumulus generated access key" >> ~/.ssh/authorized_keys
```

