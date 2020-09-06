#!/bin/bash

if [[ "$#" -ne 3 ]]; then
    exit 1
fi

python3.5 wiki_indexer.py $1 $2 $3