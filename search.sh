#!/bin/bash

if [[ "$#" -ne 2 ]]; then
	echo "Needs only two argument for search "
    exit 1
fi

#1 -  outputdir for the indexes
#2 - query.txt
#3 - query_op.txt
python3.5 wiki_search.py $1 $2 $3