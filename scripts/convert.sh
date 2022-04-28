#!/bin/bash

if [ "0" -eq "$#" ]; then
	echo "No input files"
	exit 1
fi

while [ "0" -ne "`grep -Eoh '#[_a-zA-Z0-9]+' $@ | wc -l`" ]; do
	sed -i -E 's/#([_a-zA-Z0-9]+)/`\1/' $@
done

sed -i -E 's/#`const/#define/' $@
sed -i -E 's/#`def/#define/' $@
sed -i -E 's/`include/#include/' $@
sed -i -E 's/`define/#define/' $@
