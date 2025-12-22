#!/usr/bin/bash

files=$(samweb -e icarus list-files "defname: run2_compression_production_v09_82_02_01_numimajority_compressed_data and run_number 9746 and first_event > 164000 and last_event < 172000")

for f in $files; do
    echo "------------------------------"
    echo "File: $f"
    path=$(samweb -e icarus locate-file "$f" | head -n 1)
    path=${path#dcache:}
    filePath="${path}/${f}"
    echo "Full Path: $filePath"
    file_info_dumper --event-list $filePath | grep 166767
done;