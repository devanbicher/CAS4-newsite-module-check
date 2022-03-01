#!/bin/bash

if [ -f cas2_modules.csv ]; then
    mv cas2_modules.csv ./cas2-backups/cas2_modules-$(date +'%m%d%y-%H%M').csv
fi

echo "HEY! Don't forget to run the script to generate the cas2 list WITH THE TERMINAL WINDOW FULL SCREEN!"
echo "The script to generate this list and copy it is: in ~/use_scripts/modulelisttocasdev.sh"

sed -e 's/  \+/,/g' cas2_modules.txt | sed 's/,$//g' | grep -v "Package,Name,Status,Version" | cut -d, -f2- > cas2_modules.csv
