singularity exec -C -B $(pwd):/wD BMR.sif bash /wD/Script/SingBlastCall.sh "$1"
#" blastn -num_threads 4 -query /wD/"$1" -db /wD/BLASTDB/RotaVDB -evalue 1e-50 -outfmt 6 | sort -k12,12gr  | awk -v N="" '{if ($2 != N) {print $0;N=$2} }' | head -n 20 | awk '{print "echo -e \""$0"\";bash /wD/Script/IdGrep.sh "$3}'  | bash "
