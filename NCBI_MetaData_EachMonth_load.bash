NaMe=$1
YeAr=$2
MoNtH=$3
export NCBI_API_KEY=$4;
export EMAIL=$5;
if [ $# -lt 5 ]
then 
        echo "usage bash "$0" TargetSpeciesName Year[1999] Month[1 to 12] NCBI_API_KEY EMAIL "
else
esearch -db nuccore -query "$NaMe""[Organism] -mindate "$YeAr""/""$MoNtH" -maxdate "$YeAr""/""$MoNtH" " | efetch -format docsum > MetaData_"$NaMe"_"$YeAr"_"$MoNtH"_"$NaMe".xml
fi
