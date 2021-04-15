$name = "ubuntu-tracenet-dev"

$description = <<'EOS'
卒業研究(案)の環境
EOS

$install_package = <<SCRIPT
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install python3-pip
sudo apt-get -y install sshpass
sudo apt-get -y install python-dev python3-dev 
sudo apt-get -y install libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev
sudo apt-get -y install git

# install mininet
git clone git://github.com/mininet/mininet
cd mininet
# git tag  # list available versions
git checkout -b mininet-2.3.0 2.3.0  # or whatever version you wish to install
cd ..
mininet/util/install.sh
SCRIPT

# vagrant configure version 2
VAGRANTFILE_API_VERSION = "2"
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    # vm name
    config.vm.hostname = $name + '.localhost'
    # ubuntu image
    config.vm.box = 'bento/ubuntu-18.04'
    # network
    config.vm.network 'private_network', ip: '10.0.0.100'
    # port forward
    config.vm.network "forwarded_port", guest: 80, host: 8888
    # share directory
    config.vm.synced_folder './', '/home/vagrant'
    # install package
    config.vm.provision 'shell', inline: $install_package

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