#!/bin/bash

# Display a welcome message using figlet
figlet -k "Dr. Jarvis"

# Source conda to activate the environment
source /home/cmpuser1/anaconda3/etc/profile.d/conda.sh

# Activate the desired conda environment
conda activate RAG

# Display some status messages
echo -e "\n"
echo "CONNECTION ESTABLISHING ..."

# Run the Python script and capture its output (the value of on_db)
python3 -m src.main


