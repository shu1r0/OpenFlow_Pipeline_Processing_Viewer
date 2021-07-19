$name = "ubuntu-tracenet-dev"

$description = <<'EOS'
<Environment to be used for graduation research>

It need the tools following:
* BOFUSS
* Mininet
EOS

# install basic libraries
# python, git ...etc
# TODO:
#    * tsharkを追加する
$install_package = <<SCRIPT
# install package
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install python3-pip
sudo apt-get -y install sshpass
sudo apt-get -y install python3.8-dev python3.8

# python upgrade
# update-alternatives causes a bug
# sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 20
# sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 10
# sudo alternatives --auto python3
python3.8 -m pip install -U pip
sudo apt-get -y remove python-pexpect python3-pexpect

sudo apt-get -y install libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev
sudo apt-get -y install git
sudo apt-get -y install curl
sudo apt-get -y install tshark
sudo apt-get -y install ubuntu-desktop

#NOTE: Should is used venv???
sudo pip3 install --upgrade pip
sudo pip3 install --upgrade pexpect
sudo pip3 install --upgrade lxml
sudo pip3 install grpcio-tools
sudo pip3 install pyshark
sudo pip3 install scapy
sudo pip3 install mininet
SCRIPT

# install mininet witch bofuss
$install_mininet = <<SCRIPT
cd module
git clone git://github.com/mininet/mininet
cd mininet
# git tag  # list available versions
git checkout -b mininet-2.3.0 2.3.0  # or whatever version you wish to install
cd ..
# mininet/util/install.sh -n3fw
mininet/util/install.sh -a

sudo apt-get -y install openvswitch-switch
sudo service openvswitch-switch start
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
sudo apt install -y python3-ryu
SCRIPT

# install faucet
# Notes:
#   * faucet configuration `` /etc/faucet/faucet.yaml ``
#@link: https://docs.faucet.nz/en/latest/tutorials/first_time.html#package-installation
$install_faucet = <<SCRIPT
sudo apt-get install -y curl gnupg apt-transport-https lsb-release
echo "deb https://packagecloud.io/faucetsdn/faucet/$(lsb_release -si | awk '{print tolower($0)}')/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/faucet.list
curl -L https://packagecloud.io/faucetsdn/faucet/gpgkey | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y faucet-all-in-one
SCRIPT


$install_onos = <<ONOS
sudo apt install -y openjdk-11-jdk

cd /opt
sudo wget -c https://repo1.maven.org/maven2/org/onosproject/onos-releases/2.5.1/onos-2.5.1.tar.gz
sudo tar xzf onos-2.5.1.tar.gz
sudo mv onos-2.5.1 onos

sudo cp /opt/onos/init/onos.initd /etc/init.d/onos
sudo cp /opt/onos/init/onos.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable onos
ONOS

#NOTE: I don't test
#@link https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
$install_mongodb = <<SCRIPT
sudo apt-get install -y gnupg
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt-get update -y
sudo apt-get install -y mongodb-org
# sudo systemctl start mongod
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
    # port forward for ONOS
    config.vm.network 'forwarded_port', guest: 8181, host: 8181
    # share directory
    config.vm.synced_folder './', '/home/vagrant'
    # config.vm.synced_folder '../tracer_net', '/home/vagrant/tracer_net'
    # config.vm.synced_folder '../ofcapture', '/home/vagrant/ofcapture'
    # install package
    config.vm.provision 'shell', inline: $install_package
    config.vm.provision 'shell', inline: $install_mininet
    config.vm.provision 'shell', inline: $install_ryu
    config.vm.provision 'shell', inline: $install_onos

    # config virtual box
    config.vm.provider "virtualbox" do |vb|
        vb.name = $name
        vb.gui = true

        vb.cpus = 2
        vb.memory = "2048"
    
        vb.customize [
            "modifyvm", :id,
            "--vram", "256", # full screen
            "--clipboard", "bidirectional", # clip board
            "--draganddrop", "bidirectional", # drag and drop
            "--ioapic", "on", # enable I/O APIC
            "--description", $description
        ]
    end
end