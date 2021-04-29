$name = "ubuntu-tracenet-dev"

$description = <<'EOS'
<Environment to be used for graduation research>

It need the tools following:
* wireshark
* BOFUSS
* Mininet
EOS

# install basic libraries
# python, git ...etc
$install_package = <<SCRIPT
# install package
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install python3-pip
sudo apt-get -y install sshpass
sudo apt-get -y install python-dev python3-dev 
sudo apt-get -y install libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev
sudo apt-get -y install git
SCRIPT

# install mininet
$install_mininet = <<SCRIPT
cd module
git clone git://github.com/mininet/mininet
cd mininet
# git tag  # list available versions
git checkout -b mininet-2.3.0 2.3.0  # or whatever version you wish to install
cd ..
mininet/util/install.sh -n
# -n3fxw

# cd $HOME/
# cd module
# sudo apt install -y scons
# git clone https://github.com/CPqD/ofdissector
# cd ofdissector/src
# export WIRESHARK=/usr/include/wireshark
# scons install
SCRIPT

$install_mininet_with_bofuss = <<SCRIPT
cd module
git clone git://github.com/mininet/mininet
cd mininet
# git tag  # list available versions
git checkout -b mininet-2.3.0 2.3.0  # or whatever version you wish to install
cd ..
mininet/util/install.sh -n3fxw
SCRIPT

# install BOFUSS (build from source)
#@link https://github.com/CPqD/ofsoftswitch13
$install_bofuss = <<SCRIPT
cd module
sudo apt-get install -y cmake libpcap-dev libxerces-c3.2 libxerces-c-dev libpcre3 libpcre3-dev flex bison pkg-config autoconf libtool libboost-dev

# Clone and build netbee
git clone https://github.com/netgroup-polito/netbee.git
cd netbee/src
cmake .
make
cd ../tools
cmake .
make
cd ../samples
cmake .
make
cd ..
sudo ./install.sh

# sudo apt-get install -y wireshark-dev
# sudo apt-get install -y scons
# export WIRESHARK=/usr/include/wireshark
SCRIPT

# install ryu 
# Libraries dependent on ryu are added here as required
$install_ryu = <<SCRIPT
pip install ryu
SCRIPT

# vagrant configure version 2
VAGRANTFILE_API_VERSION = "2"
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    # vm name
    config.vm.hostname = $name + '.localhost'
    # ubuntu image
    config.vm.box = 'bento/ubuntu-18.04'  # error
    # config.vm.box = 'bento/ubuntu-16.04'
    # network
    config.vm.network 'private_network', ip: '10.0.0.100'
    # port forward
    config.vm.network "forwarded_port", guest: 80, host: 8888
    # share directory
    config.vm.synced_folder './', '/home/vagrant'
    # install package
    config.vm.provision 'shell', inline: $install_package
    config.vm.provision 'shell', inline: $install_mininet_with_bofuss
    config.vm.provision 'shell', inline: $install_ryu

    # config virtual box
    config.vm.provider "virtualbox" do |vb|
        vb.name = $name
        vb.gui = true

        vb.cpus = 1
        vb.memory = "1024"
    
        vb.customize [
            "modifyvm", :id,
            # "--vram", "256", # full screen
            "--clipboard", "bidirectional", # clip board
            "--draganddrop", "bidirectional", # drag and drop
            "--ioapic", "on", # enable I/O APIC
            "--description", $description
        ]
    end
end