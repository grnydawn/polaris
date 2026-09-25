# shellcheck shell=bash
# Shell environment for the nightly cron jobs on frontier, sourced by
# launch_all.sh.  Cron starts with almost no environment, so this provides
# what deploy.py and the tasks need before any Polaris environment exists.

# cron has no `module`: crontab.template runs bash with no -l and
# nothing sources a profile.  /etc/profile provides both lmod and a
# MODULEPATH.  The `|| true` is required rather than cautious:
# /etc/profile returns non-zero part way through, and launch_all.sh
# sources this file under `set -e`.
# shellcheck disable=SC1091
source /etc/profile || true

module load cray-python git-lfs

# compute nodes reach CDash and GitHub only through the proxy; jobs inherit
# these from the submitting environment
export all_proxy=socks://proxy.ccs.ornl.gov:3128/
export ftp_proxy=ftp://proxy.ccs.ornl.gov:3128/
export http_proxy=http://proxy.ccs.ornl.gov:3128/
export https_proxy=http://proxy.ccs.ornl.gov:3128/
export no_proxy='localhost,127.0.0.0/8,*.ccs.ornl.gov'
