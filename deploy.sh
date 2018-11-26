#!/usr/bin/env bash

#!/bin/bash

OLD_PWD=$(pwd)

# Copy the app code to a temporal location
rm -rf /tmp/pysica
echo "Copying the app code..."
rsync -ar ${OLD_PWD}/ /tmp/pysica
cd /tmp/pysica
echo "Copying the app code... DONE"

# Remove unused files
rm -rf .env docker test .git .idea
rm conf/*.cfg .gitignore pysica_api.py *.pyc  .gitignore

sed -i 's/\/tmp\/cache/\/var\/log\/pysica\/cache/g' default/server.default.cfg
sed -i 's/"DEBUG" : true/"DEBUG" : false/g' default/server.default.cfg

echo "Compressing server application... "
zip -r ../pysica.zip *
echo "Compressing server application... DONE"

echo "Moving result to docker directory..."
cd $OLD_PWD
mv /tmp/pysica.zip docker/configs/pysica.zip
version=$(head -1 VERSION | awk '{sub(/v/,"",$1); print $1}')

# Getting pip install script
wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py -O /tmp/pysica/get-pip.py
check_changes=$(diff docker/configs/get-pip.py /tmp/pysica/get-pip.py)
if [[ "$?" != "0" ]]; then
  echo "Pip installator has changed"
  mv /tmp/pysica/get-pip.py docker/configs/get-pip.py
fi
echo "Moving result to docker directory... DONE"

echo "Cleaning..."
rm -rf /tmp/pysica
echo "Done."
echo "Now you can build the new docker image using the following command"
echo "sudo docker build -t fikipollo/pysica:${version}  -t fikipollo/pysica:latest ."
