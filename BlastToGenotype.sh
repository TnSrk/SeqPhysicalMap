if [ $# -eq 4 ]
then
blastn -num_threads 4 -query "$1" -db $2 -perc_identity $3 -evalue 1e-50 -outfmt 6 |\
        sort -k12,12gr  | awk -v N="" '{if ($2 != N) {print $0;N=$2} }' | head -n $4 |\
        awk '{print "echo -e \""$0"\";bash MetadataGrep.sh "$2}'  | bash
else
        echo "USAGE: bash "$0" QUERY_file_path BLAST_DB_PATH IDENTITY_CUTOFF Results_Number"
fi      
