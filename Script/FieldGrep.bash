ptt=$1
field=$2
if [ $# == 3 ]
then
	grep -m $3 "<""$field"">.*"$ptt".*</""$field"">" Metadata_1line.xml | sed "s/> />\n /g" 

else 

	grep  "<""$field"">.*"$ptt".*</""$field"">" Metadata_1line.xml | sed "s/> />\n /g" 
fi
