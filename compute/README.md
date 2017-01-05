# Compute Node - Vagrant

This vagrant deployment enable the creation of a compute node for PyFr and OpenFoam.

## Configurations

Environment variables can be used to control the VM creation.

COMPUTE_NODE_IP: 
  Set the private IP that the VM will use. 
  By default the ip is 192.168.100.100

## Creating the Compute node

```sh
$ cd HPCCloud-deploy/compute
$ vagrant up
```

## Register node to HPCCloud

- Go to your HPCCloud server (http://localhost:8888)
- Preferences
  - Cluster [+]
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
$ vagrant ssh
$ sudo -iu demo
$ mkdir -p ~/.ssh 
$ echo "ssh-rsa [...] cumulus generated access key" >> ~/.ssh/authorized_keys
```




