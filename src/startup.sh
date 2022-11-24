#!/bin/bash
apt-get -y update
apt-get -y install zbar-tools
gunicorn --bind=0.0.0.0 --timeout 600 --worker-class eventlet -w 1 app:app