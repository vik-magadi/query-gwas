#!/bin/bash
set -e -x -o pipefail
dx download $db_id
dx download $txt_id 
db_name=`dx describe --json $db_id | jq -r .name`
txt_name=`dx describe --json $txt_id | jq -r .name`
docker load -i flask_docker.tgz
docker run -p 443:5000 --name gwas_container -v /home/dnanexus:/usr/src/app/data -e db_name=$db_name -e txt_name=$txt_name flask_docker

