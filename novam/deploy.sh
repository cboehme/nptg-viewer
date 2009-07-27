#!/bin/bash

python setup.py bdist_egg

EGG=$( ls -1 dist | tail -n 1 )

scp dist/$EGG mmercia@quirm.de:
ssh mmercia@quirm.de webapps/nptg/update.sh $EGG
