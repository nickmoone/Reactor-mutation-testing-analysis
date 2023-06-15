#! /bin/bash

# Check if number of arguments is correct.
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path to python scripts folder> <path to results folder>"
    exit 1
fi

# Loop over each sub folder in projects folder.
for dir in $2/*; do
    echo $dir
    python3 $1/count_methods.py $dir $dir/count_methods.csv
done

python3 $1/combine_count_methods.py $2 $2/count_methods.csv
