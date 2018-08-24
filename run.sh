#!/bin/bash

nohup redis-server --requirepass 123456 > redis.log 2>&1 &
sleep 5s

nohup python crawler_booter.py --usage crawler common > crawler.log 2>&1 &
nohup python scheduler_booter.py --usage crawler common > crawler_scheduler.log 2>&1 &
nohup python crawler_booter.py --usage validator init > init_validator.log 2>&1 &
nohup python crawler_booter.py --usage validator https > https_validator.log 2>&1&
nohup python scheduler_booter.py --usage validator https > validator_scheduler.log 2>&1 &
nohup python squid_update.py --usage https --interval 3 > squid_update.log 2>&1 &

mkdir -p /var/cache/squid
rm -rf /var/run/squid.pid
if [ $PORT ]; then
	echo ======== Heroku service ========
	nohup squid -N -d1 > squid.log 2>&1 &
	python app_booter.py --port $PORT
else
	echo ========== normal use ==========
	squid -N -d1
fi
