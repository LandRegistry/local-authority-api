#!/bin/bash
# Script for running boundary updates in Pre-prod/Prod
cd /opt/landregistry/applications/llc-local-authority-api/
source virtualenv/bin/activate
source settings.conf
source deploy.conf
pip install -r source/requirements.txt
cd source

python3 manage.py update_boundaries