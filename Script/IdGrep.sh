grep -m 1 "$1""</OSLT>" -B 100 -A 100 /wD/Metadata.xml | grep -e "<CreateDate>" -e "<Extra>" -e "<SubName>" -e "<Title>" -e "<SubType>" -e "</Id>" -e "$1""</OSLT>" | grep -m 1 "$1""</OSLT>" -B 6 
