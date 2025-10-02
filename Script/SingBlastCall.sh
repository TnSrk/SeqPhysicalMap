echo > /wD/blastn_out.tab;
blastn -num_threads 4 -query /wD/"$1" -db /wD/BLASTDB/VDB -perc_identity 97.0 -evalue 1e-50 -outfmt 6 | sort -k12,12gr | sort -u -k2,2 | awk -v N="" '{if ($2 != N) {print $0;N=$2} }' | head -n 500 | awk '{print "echo -e \""$0"\" >> /wD/blastn_out.tab;bash /wD/Script/IdGrep.sh "$2}'  | bash 
