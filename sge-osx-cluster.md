# Installation of SGE on OSX

This guide will go through several steps that are needed in order to install
Sun Grid Engine on OSX.

`emacs` is used below as the editor but you can use any one you want.

## Prerequisites

Installing the equivalent of __build-essential__ on linux.

    $ sudo xcode-select --install

Create a library alias for __pam/pam_appl.h__

    $ sudo ln -s /usr/include/security /usr/include/pam

Configuring your shell environment

    $ emacs ~/.profile

        # Used as basepath for SGE
        export SGE_ROOT=/opt/sge

        # Used at runtime + installation
        export SGE_CELL=default
        export SGE_CLUSTER_NAME=melmac
        export SGE_QMASTER_PORT=6444
        export SGE_EXECD_PORT=6445

        # Add sge tools to the path
        export PATH=$PATH:$SGE_ROOT/bin/darwin-x64:$SGE_ROOT/utilbin/darwin-x64

    $ source ~/.profile

Configure your ssh environment

    $ emacs ~/.ssh/environment

        SGE_ROOT=/opt/sge
        PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/X11/bin:/opt/sge/bin/darwin-x64:/opt/sge/utilbin/darwin-x64
        SGE_CELL=default
        SGE_CLUSTER_NAME=melmac
        SGE_QMASTER_PORT=6444
        SGE_EXECD_PORT=6445

    $ sudo emacs /etc/sshd_config

        #PermitUserEnvironment no
        PermitUserEnvironment yes

Configuring your network

    $ hostname # => your host name
    $ ifconfig # => Find your IP, you can also do this from the Network panel in System Preferences
    $ sudo emacs /etc/hosts

        # Add your hostname with your IP so they are not bound to localhost, e.g:
        201.10.5.1    hal hal.local

## Download and build Grid Engine

    $ cd /tmp
    $ curl http://iweb.dl.sourceforge.net/project/gridscheduler/GE2011.11p1/GE2011.11p1.tar.gz -O
    $ tar xvfz GE2011.11p1.tar.gz
    $ cd GE2011.11p1/source

    $ ./aimk -no-java -no-jni -spool-classic -no-dump -no-secure -only-depend
    $ ./scripts/zerodepend
    $ ./aimk -no-java -no-jni -spool-classic -no-dump -no-secure depend
    $ ./aimk -no-java -no-jni -spool-classic -no-dump -no-secure -no-qmon -no-qtcsh

## Install SGE into your $SGE_ROOT

    $ sudo mkdir -p $SGE_ROOT && chown $USER $SGE_ROOT
    $ cd /tmp/GE2011.11p1/source
    $ ./scripts/distinst -local -all -noexit

Note: It should complain for `qtcsh`, `qmon` as you did not build them.

## Configure SGE

    $ cd $SGE_ROOT
    $ cat inst_sge | grep -v PreInstallCheck > inst_sge_no_check
    $ chmod +x inst_sge_no_check

    # You may want to run them as root (authors did not)
    # You can stop and restart this setup as many times as you need.
    # It's mostly pressing enter with a few exceptions noted below:
    $ ./inst_sge_no_check -m

    ...
        Enter cell name [default]

        Adding admin and submit hosts
        -----------------------------

        Please enter a blank seperated list of hosts.

        Stop by entering <RETURN>. You may repeat this step until you are
        entering an empty list. You will see messages from Grid Engine
        when the hosts are added.

        Host(s): >>> your host name (melmac for me)
        adminhost "melmac" already exists
        melmac added to submit host list

        =======================================================================

        Scheduler Tuning
        ----------------

        The details on the different options are described in the manual.

        Configurations
        --------------
        1) Normal
                  Fixed interval scheduling, report limited scheduling information,
                  actual + assumed load

        2) High
                  Fixed interval scheduling, report limited scheduling information,
                  actual load

        3) Max
                  Immediate Scheduling, report no scheduling information,
                  actual load

        Enter the number of your preferred configuration and hit <RETURN>!
        Default configuration is [1] >> 3

        We're configuring the scheduler with >Max< settings!
        Do you agree? (y/n) [y] >>
    ...

    # You may want to run them as root (I did not)
    $ ./inst_sge_no_check -x

    ...

If you've restarted or rerun the setup checks above you may want
to also restart the SGE processes. You can kill the processes
from Activity Monitor or `ps`. Start up the processes again with the
commands in the next section.

## Running SGE after a reboot or a `kill -9`

    $SGE_ROOT/default/common/sgemaster
    $SGE_ROOT/default/common/sgeexecd

## Configuring python

    $ cd /tmp
    $ git clone https://github.com/Kitware/HPCCloud-deploy.git
    $ cd HPCCloud-deploy
    $ sudo pip install -r requirements-cluster.txt

Note: Not tested on OSX 10.11 (El Capitan).

## Registering your OSX cluster

1. Go to: http://localhost:8888
2. Login or Register
    - Use a default user:
    user: `user001`
    pass: `user001001`
3. Click on your user (Upper right corner)
4. Click on the + for "Clusters"
5. Set a name for that configuration
6. Click on that name in the list of Clusters
    You should fill:

        hostname                     : [the hostname of your machine]
        username                     : [your username]
        Simulation output directory  : [anywhere, absolute path]
        Hydra executable path        : [Hydra executable path, absolute path]
        ParaView install directory   : [Paraview execytable, probably: /Applications/paraview.app]

    => Save

7. Copy the "echo ..." command line and paste it into a terminal.
8. Click on the "Test" button
9. If success, then you can start using that cluster to run jobs.