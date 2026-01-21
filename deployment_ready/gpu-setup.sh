#!/bin/bash
# ------------------------------------------------------
# GPU-READY INSTANCE PREPARATION SCRIPT (DOCUMENTATION)
# ------------------------------------------------------
# Purpose:
# Prepare an Ubuntu-based EC2 instance for future GPU- accelerated Docker workloads.
#
#
# Tested target OS:
# - Ubuntu 20.04 / 22.04
#
# Expected EC2 Types:
# - g4dn.xlarge
# - g5.xlarge
# - p3 / p4 series
# ------------------------------------------------------

set -e

echo "Checking for NVIDIA GPU already exist in system"
lspci | grep -i nvidia || echo "No NVIDIA GPU detected"
#if not then, installing the nvidia drivers

sudo apt update

echo "Installing NVIDIA drivers"
sudo apt install -y nvidia-driver-535

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
sudo systemctl restart docker

nvidia-smi #to validate the installation after system reboot
