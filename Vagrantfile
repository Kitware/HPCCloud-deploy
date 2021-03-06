# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
require 'fileutils'

# We need the ansible provisioner with galaxy support
Vagrant.require_version ">= 1.8.1"
Vagrant.configure(2) do |config|

  dev = ENV.has_key?('DEVELOPMENT') ? ENV['DEVELOPMENT'] : false
  demo = ENV.has_key?('DEMO') ?  ENV['DEMO'] : false
  cumulus = ENV.has_key?('CUMULUS') ?  ENV['CUMULUS'] : false
  vm_name = ENV.has_key?('VM_NAME') ? ENV['VM_NAME'] : "hpccloud-vm"
  hpccloud_password = 'letmein'

  config.vm.box = "ubuntu/trusty64"

  girder_host_port = ENV["GIRDER_HOST_PORT"] || 8080
  hpccloud_host_port = ENV["HPCCLOUD_HOST_PORT"] || 8888

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8888" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  if !cumulus
    config.vm.network "forwarded_port", guest: 80, host: hpccloud_host_port
  end
  config.vm.network "forwarded_port", guest: 8080, host: girder_host_port


  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Note:  not currently possible to set ower/group of these files
  # after provisioning (See: https://github.com/mitchellh/vagrant/issues/936)
  # This means we need to set user and owner to UID/GUID which get created
  # later (when we make the hpccloud and celery users)
  if dev
    for f in ["cumulus", "hpccloud"]
      if File.directory?("../" + f)
        config.vm.synced_folder "../#{f}", "/opt/hpccloud/" + f.downcase,
                                owner: 1002, group: 1003
      end
    end
  end

  if cumulus
    config.vm.synced_folder '.', '/vagrant', disabled: true
  end

  config.vm.define vm_name do |node|
  end

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  # Dynamically allocate memory and cpus,
  # see https://stefanwrobel.com/how-to-make-vagrant-performance-not-suck
  config.vm.provider "virtualbox" do |v|
    host = RbConfig::CONFIG['host_os']

    # Give VM 1/4 system memory & access to 1/2 of the cpu cores on the host
    if host =~ /darwin/
      cpus = `sysctl -n hw.ncpu`.to_i
      cpus = cpus / 2
      # sysctl returns Bytes and we need to convert to MB
      mem = `sysctl -n hw.memsize`.to_i / 1024 / 1024 / 4
    elsif host =~ /linux/
      cpus = `nproc`.to_i
      cpus = cpus / 2
      # meminfo shows KB and we need to convert to MB
      mem = `grep 'MemTotal' /proc/meminfo | sed -e 's/MemTotal://' -e 's/ kB//'`.to_i / 1024 / 4
    else # Guess!
      cpus = 2
      mem = 4096
    end

    v.customize ["modifyvm", :id, "--memory", mem]
    v.customize ["modifyvm", :id, "--cpus", cpus]
    v.customize ["modifyvm", :id, "--nictype1", "virtio"]
    v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]

  end


  # Setup HPCCloud/cumulus stack
  config.vm.provision "ansible" do |ansible|
    ansible.groups = {
      "all" => [vm_name],
      "cumulus" => [vm_name],
      "girder" => [vm_name],
      "mongo" => [vm_name]
    }

    if !cumulus
      ansible.groups["hpccloud"] = [vm_name]
      ansible.groups["pyfr"] = [vm_name]
    end

    ansible.verbose = "vv"
    ansible.extra_vars = {
      default_user: "vagrant",
      development: dev,
      hpccloud_password: hpccloud_password,
      demo: demo,
      cumulus: cumulus,
      girder_bind_interface: "0.0.0.0"
    }

    ansible.galaxy_role_file = "ansible/requirements.yml"

    ansible.playbook = "ansible/site.yml"
  end

  config.vm.provision "shell", inline: "sudo service celeryd restart", run: "always"
  config.vm.provision "shell", inline: "sudo service girder restart", run: "always"

  # Should we also deploy a "cluster" on the VM
  if demo
    # Create temp directory
    dir = Dir.mktmpdir()

    # First download cumulus so we have access to the playbooks
    config.vm.provision "ansible" do |ansible|

      # If there is a better way to run playbook aganst localhost let
      # me know!
      ansible.raw_arguments = ['--limit=localhost',
        '--inventory-file=localhost,',
        '--connection=local']

      ansible.verbose = "vv"
      ansible.extra_vars = {
        tmpdir: dir
      }
      ansible.playbook = "demo/cumulus.yml"
    end

    # Setup SGE using cumulus playbook
    config.vm.provision "ansible" do |ansible|
      ansible.groups = {
        "master" => [vm_name]
      }

      ansible.verbose = "vv"
      ansible.extra_vars = {
        default_user: "vagrant",
        tmpdir: dir
      }
      ansible.playbook = "#{dir}/cumulus/cumulus/ansible/tasks/playbooks/gridengine/site.yml"

      # We need to ensure this path exists when this file is loaded. It will
      # be populated with correct content by an ansible role, however,
      # Vagrant wants it to exist now!
      dirname = File.dirname(ansible.playbook)
      unless File.directory?(dirname)
        FileUtils.mkdir_p(dirname)
      end
      FileUtils.touch(ansible.playbook)
    end

    # Now setup demo configuration
    config.vm.provision "ansible" do |ansible|
      # For PyFR role
      ansible.galaxy_role_file = "demo/requirements.yml"

      ansible.groups = {
        "users" => [vm_name],
        "paraview" => [vm_name],
        "fixtures" => [vm_name],
        "pyfr" => [vm_name]
      }

      ansible.verbose = "vv"
      ansible.extra_vars = {
        default_user: "vagrant",
        hpccloud_password: hpccloud_password
      }
      ansible.playbook = "demo/site.yml"
    end

    # Finally clean up temp directory
    config.vm.provision "ansible" do |ansible|
      ansible.raw_arguments = ['--limit=localhost',
        '--inventory-file=localhost,',
        '--connection=local']

      ansible.verbose = "vv"
      ansible.extra_vars = {
        tmpdir: dir
      }
      ansible.playbook = "demo/cumulus_cleanup.yml"
    end
  end
end
