grep -E "$1""</"$2">" -A 15 -B 2 Metadata.xml | grep -e "<CreateDate>" -e "<Extra>" -e "<SubName>" -e "<Title>" -e "<SubType>" -e "<Strain>" -e "<Id>" 
