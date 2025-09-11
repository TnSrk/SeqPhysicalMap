cat  |\
      	bash Script/BlockXml2Json.sh |\
       	tr -d '\\' | sed "s/\([A-z]\)\:.*\"/\1\"/"   |\
      	jq -r '.[] | [.collection_date,.CreateDate,.country,.Id]| @csv' | tee filter_out.json |\
       	awk -F "," '{if ($3=="") {$3="Unspecified"};if ($1=="") {$1="1970-01-02" };print $1","$2","$3","$4 }' |\
       	bash Script/DatetoEpoch.sh | awk -F "," '{print $0","$3","}' |\
       	sed "s/:.*,/,/g" | tr " " "_" > GrepResults.csv; cut -d "," -f 3 GrepResults.csv |\
       	sort -u > CountryList.txt;
	#grep  -i -f CountryList.txt worldcities.csv | sort -t "," -u -k5,5 |\
	echo -n "" > CountryCoordinates.txt;
	for i in $(more CountryList.txt);
		do 
		grep -m 1  \"$i\" worldcities.csv |\
       		awk -F "," -v N=$i '{gsub("\"","",$0);print "s/," N ",/," $3 "," $4 ",/" }' >> CountryCoordinates.txt;
		done;
       	echo "s/Unspecified/-18.249689,77.929869/" >> CountryCoordinates.txt; 
	sed -f CountryCoordinates.txt GrepResults.csv | awk -F ',' '{print $6 "," $3 "," $4 "," $1 }' > input.csv
