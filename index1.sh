#!/usr/bin/env bash

if [[ "$#" -ne 2 ]]; then
    exit 1
fi

# 1- output directory containing all the index files
# 2- stat index file

file="../WikiDump/data_urls1.txt"
iter=1
status=0
titleNum=0
echo $1
echo $2

# while IFS= read -r url
# do
#     url="${url#"${url%%[![:space:]]*}"}"
#     echo "line $url"
#     wget -c "$url"
#     xmlZip=`find ./ -name "*.bz2"`
#     bzip2 -d $xmlZip
#     echo "$xmlZip"
#     # xmlFile=`find ./ -name "enwiki*"`
#     xmlFile=${xmlZip::-4}
#     echo "$xmlFile"
#     t=`python3.5 wiki_indexer.py $xmlFile $1 $2 $iter $status $titleNum  2>&1 > /dev/null`
#     titleNum=t
#     if [[ "$iter" -eq 2 ]]; then
#         break
#     fi
#     iter=$((iter + 1))
# done <"$file"

status=1
t=`python3.5 wiki_indexer.py $xmlFile $1 $2 $iter $status $titleNum  2>&1 > /dev/null`
