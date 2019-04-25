#!/bin/bash
mkdir -p /tmp/outsource/logs/
nohup COMMAND_NAME > /tmp/outsource/logs/LOG_NAME 2>&1 &
