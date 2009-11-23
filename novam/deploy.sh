#!/bin/bash

python2.5 setup.py bdist_egg

EGG=$( ls -1 dist | tail -n 1 )

scp dist/$EGG kofje:
#ssh mmercia@quirm.de webapps/novam/update.sh $EGG
