#!/bin/bash -l
#SBATCH  --nodes=1
#SBATCH  --qos=high
#SBATCH  --time 02:00:00

source /etc/bashrc

exec bash ${RUNSCRIPT_DIR}/run_omega_cdash.sh
