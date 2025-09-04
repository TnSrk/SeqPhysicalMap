grep -m 1 "$1""</OSLT>" -B 40 Metadata.xml | grep -e "<CreateDate>" -e "<Extra>" -e "<SubName>" -e "<Title>" -e "<SubType>" | head -n 5
