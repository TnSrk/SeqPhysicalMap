NaMe=$1
YeAr=$2
MoNtH=$3
export NCBI_API_KEY=$4;
export EMAIL=$5;
esearch -db nuccore -query "$NaMe""[Organism] -mindate "$YeAr""/""$MoNtH" -maxdate "$YeAr""/""$MoNtH" " | efetch -format docsum > /workplace/ALL_"$YeAr"_"$MoNtH"_"$NaMe"_metadata.xml
