#!/bin/bash

mv cas4modules-*.csv module-lists/

curpath=$(pwd)
cd /var/www/drupal/sites

drush pm-list --type=module --format=csv --fields=name,status,version > $curpath"/cas4modules-$(date +'%m%d%y-%H%M').csv"

