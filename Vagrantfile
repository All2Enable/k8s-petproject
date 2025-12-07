Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.ssh.insert_key = true

  # Хосты
  $setup_hosts = <<-SHELL
cat <<EOF >> /etc/hosts
192.168.56.10 k8s-master
192.168.56.11 k8s-worker-1
192.168.56.12 k8s-worker-2
EOF
SHELL

  # --- Worker1 ---
  config.vm.define "worker1" do |node|
    node.vm.hostname = "k8s-worker-1"
    node.vm.network "private_network", ip: "192.168.56.11"
    node.vm.provider "virtualbox" do |vb|
      vb.memory = 4096  
      vb.cpus = 2       
    end
    node.vm.provision "shell", inline: $setup_hosts
  end

  # --- Worker2 ---
  config.vm.define "worker2" do |node|
    node.vm.hostname = "k8s-worker-2"
    node.vm.network "private_network", ip: "192.168.56.12"
    node.vm.provider "virtualbox" do |vb|
      vb.memory = 4096  
      vb.cpus = 2       
    end
    node.vm.provision "shell", inline: $setup_hosts
  end

  # --- Master ---
  config.vm.define "master" do |master|
    master.vm.hostname = "k8s-master"
    master.vm.network "private_network", ip: "192.168.56.10"
    master.vm.provider "virtualbox" do |vb|
      vb.memory = 8192  
      vb.cpus = 2       
    end
    master.vm.provision "shell", inline: $setup_hosts

    master.vm.provision "shell", inline: <<-SHELL
      echo "Preparing SSH keys directory..."
      mkdir -p /home/vagrant/keys
      chmod 700 /home/vagrant/keys
      chown vagrant:vagrant /home/vagrant/keys

      echo "Copying private keys from Vagrant directory..."

      cp /vagrant/.vagrant/machines/worker1/virtualbox/private_key \
         /home/vagrant/keys/k8s-worker-1.key

      cp /vagrant/.vagrant/machines/worker2/virtualbox/private_key \
         /home/vagrant/keys/k8s-worker-2.key

      cp /vagrant/.vagrant/machines/master/virtualbox/private_key \
         /home/vagrant/keys/k8s-master.key

      chmod 600 /home/vagrant/keys/*.key
      chown vagrant:vagrant /home/vagrant/keys/*.key
    SHELL

    master.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y ansible

      ansible-galaxy collection install kubernetes.core

      cp -r /vagrant/ansible /home/vagrant/ansible-project
      chown -R vagrant:vagrant /home/vagrant/ansible-project

      cd /home/vagrant/ansible-project
      sudo -u vagrant ansible-playbook -i inventory.ini playbook.yml
    SHELL
  end
end
