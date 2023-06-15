#! /bin/bash

# Check if number of arguments is correct.
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path to python scripts folder> <path to results folder>"
    exit 1
fi

# Simultaniously iterate folders in /reactive and /no-reactive.
# Results are placed in the reactive folder.
for dir1 in $2/*; do
    echo $dir1
    python3 $1/compare_coverage.py $dir1 $dir1/compare_coverage.csv
done

python3 $1/combine_compare_coverage.py $2 $2/../compare_coverage.csv
