#!/bin/bash
mkdir -p /tmp/outsource/jobs/JOB_NAME
cd /tmp/outsource/jobs/JOB_NAME

mkdir -p /tmp/outsource/logs/
nohup COMMAND_NAME > /dev/null 2>&1 &
