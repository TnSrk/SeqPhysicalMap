Gi=$1
export NCBI_API_KEY=$2;
export EMAIL=$3;
$(esearch -db nuccore -query ""$Gi"[GI]" | efetch -format fasta >>  NCBI_load.fasta && echo "$Gi" >> SUCCEED_GI.log) || $(echo -n "$Gi" >> FAILED_GI.log;date >> FAILED_GI.log)
