up:
	# cp -R ../ofcapture module/ofcapture
	# cp -R ../tracer_net module/tracer_net
	# rm -rf module/tracer_net/mininet*
	# cd view; npm run build; cd ..
	vagrant up 2>&1 | tee log/vagrant-`date +'%Y-%m-%d-%H-%M'`.log

reload:
	vagrant halt
	vagrant up

halt:
	vagrant halt

destroy:
	vagrant destroy -f
	# rm -rf module/*
	mv .bash_history log/vagrant-bash_history-`date +'%Y-%m-%d-%H-%M'`.log
	mv .mininet_history log/vagrant-mininet_history-`date +'%Y-%m-%d-%H-%M'`.log

run:
	make clean
	cd src; sudo python3.8 tracing_of_pipeline.py

clean:
	sudo mn -c
	
reference:
	sphinx-apidoc -f -o docs/source/references/ ./src/