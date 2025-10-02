cd /wD;
ptt=$1
field=$2
if [ $# == 3 ]
then
        cat Metadata.xml | tr -d "\n"  | sed "s/<DocumentSummary>/#<DocumentSummary>/g" | tr "#" "\n" | grep "<Id>"  | grep -m $3 "<""$field"">.*"$ptt".*</""$field"">"  | sed "s/> />\n /g"

else

        cat Metadata.xml | tr -d "\n"  | sed "s/<DocumentSummary>/#<DocumentSummary>/g" | tr "#" "\n" | grep "<Id>" | grep  "<""$field"">.*"$ptt".*</""$field"">" | sed "s/> />\n /g"
fi
