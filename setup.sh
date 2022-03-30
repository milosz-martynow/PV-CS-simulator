#!/bin/bash

function extract_values_from_config () {

  local config_toml=$1
  local toml_key=$2
  local val

  val=$(grep $toml_key $config_toml)
  val=($val)
  val=${val[-1]}
  val="${val//\"}"

  echo "$val"
}

config_file="config.toml"
echo "[INFO] $config_file will be loaded."

python_path=$(extract_values_from_config $config_file "python_path")
python_libs_installation=$(extract_values_from_config $config_file "python_libraries_installation")
rabbitmq_installation=$(extract_values_from_config $config_file "rabbitmq_installation")

# INSTALLATION OF PYTHON PACKAGES:
if $python_libs_installation -eq true
then
  if ! command -v pip &> /dev/null
  then
    echo "[INFO] pip could not be found."
    echo "[INFO] pip installation will started after password passing (due to sudo)."
    sudo sudo apt-get install python3-pip
  else
    echo "[INFO] pip is already installed."
  fi

  echo "[INFO] Python from $python_path will be used for application setup."

  echo "[INFO] pip upgrade check."
  $python_path -m pip install --upgrade pip
  echo "[INFO] pip is actual."

  echo "[INFO] Installing required python packages."
  $python_path -m pip install -r requirements.txt
  echo "[INFO] Required packages are installed."
  echo "[INFO] Please reset the terminals."
fi

#  INSTALLATION OF RABBITMQ
#  Software producent script
if $rabbitmq_installation -eq true
then
  echo "[INFO] RabbitMQ will be installed"
  sudo apt-get install curl gnupg apt-transport-https -y

  ## Team RabbitMQ's main signing key
  curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null
  ## Cloudsmith: modern Erlang repository
  curl -1sLf https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/gpg.E495BB49CC4BBE5B.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg > /dev/null
  ## Cloudsmith: RabbitMQ repository
  curl -1sLf https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/gpg.9F4587F226208342.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg > /dev/null

## Add apt repositories maintained by Team RabbitMQ
sudo tee /etc/apt/sources.list.d/rabbitmq.list <<EOF
## Provides modern Erlang/OTP releases
##
deb [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/deb/ubuntu bionic main
deb-src [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/deb/ubuntu bionic main

## Provides RabbitMQ
##
deb [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/deb/ubuntu bionic main
deb-src [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/deb/ubuntu bionic main
EOF

  ## Update package indices
  sudo apt-get update -y

  ## Install Erlang packages
  sudo apt-get install -y erlang-base \
                          erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
                          erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
                          erlang-runtime-tools erlang-snmp erlang-ssl \
                          erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl

  ## Install rabbitmq-server and its dependencies
  sudo apt-get install rabbitmq-server -y --fix-missing
fi