NaMe=$1
export NCBI_API_KEY=$2;
export EMAIL=$3;
if [ $# -lt 3 ]
then 
        echo "usage bash "$0" TargetSpeciesName NCBI_API_KEY EMAIL "
else
esearch -db nuccore -query "$NaMe""[Organism]" | efetch -format docsum > MetaData_"$NaMe".xml
fi
