#!/bin/bash
nohup python -m SimpleHTTPServer 3000 > /tmp/logs 2>&1 &
