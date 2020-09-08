#!/usr/bin/env bash

if [[ "$#" -ne 2 ]]; then
    exit 1
fi

# 1- output directory containing all the index files
# 2- stat index file

file="../WikiDump/data_urls1.txt"
iter=1

echo $1
echo $2

while IFS= read -r url
do
    # url="${url#"${url%%[![:space:]]*}"}"
    # echo "line $url"
    # wget -c "$url"
    echo "$iter"
    xmlZip=$(find ./ -name "*.bz2")
    echo "$xmlZip"
    bzip2 -d "$xmlZip"
    xmlFile=`find ./ -name "enwiki*"`
    echo "$xmlFile"
    python3.5 wiki_indexer.py $xmlFile $1 $2 $iter
    if [[ "$iter" -eq 1 ]]; then
        break
    fi
    iter=$((iter + 1))
done <"$file"
