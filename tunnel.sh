#!/usr/bin/bash
ssh ubuntu@benteveo.com -i /home/wasap/.ssh/parexaws -L 3306:127.0.0.1:3306 -N &
