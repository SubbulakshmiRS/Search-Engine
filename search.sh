#!/bin/bash

if [[ "$#" -ne 2 ]]; then
	echo "Needs only two argument for search "
    exit 1
fi

python3.5 wiki_search.py $1 $2