up:
	vagrant up 2>&1 | tee log/vagrant-`date +'%Y-%m-%d-%H-%M'`.log

destroy:
	vagrant destroy -f
	rm -rf module/*
	mv .bash_history log/vagrant-bash_history-`date +'%Y-%m-%d-%H-%M'`.log
	mv .mininet_history log/vagrant-mininet_history-`date +'%Y-%m-%d-%H-%M'`.log