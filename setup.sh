#!/bin/bash

docker build -t haipproxy .  
docker tag haipproxy registry.heroku.com/ipproxy-pool/web
docker push registry.heroku.com/ipproxy-pool/web:latest
heroku container:release web -a ipproxy-pool
