#!/bin/sh
virtualenv virt
. virt/bin/activate
pip install -r requirements.txt

npm install
export PATH=node_modules/.bin:$PATH
bower install
