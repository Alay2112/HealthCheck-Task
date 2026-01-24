#!/bin/bash

set -euo pipefail

echo "Checking for NVIDIA GPU on this machine..."
if ! lspci | grep -i nvidia; then
  echo "No NVIDIA GPU detected. Skipping driver + toolkit installation."
  exit 0
fi

sudo apt update

echo "Installing NVIDIA drivers"
# here since nvidia-driver-535 may not exist in all ubuntu versions so I'm using autoinstall
sudo apt-get install -y ubuntu-drivers-common
sudo ubuntu-drivers autoinstall

#after installation of any drivers there is system reboot needed so do a reboot after completing last step

echo "Installing NVIDIA Container Toolkit" # it is importent for running docker containers.

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.gpg] https://#g' | \
sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit

echo "Restarting Docker Service"
sudo systemctl daemon-reload
sudo systemctl restart docker

#run 'nvidia-smi' command to validate the installation after system reboot
