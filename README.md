# SeqPhysicalMap
container definition file and related scripts for searching related sequences or metadata of existing record then visualize by plotting to world map or specific country map.

Input
- Existing known species/strains DNA sequences for databse creation
  format = fasta
  
- Metadata of the species
  format = json or xml or tsv or csv **current=json

- Lat/Lon for conutry/lower level area
  format = csv

- Filter criteria
  format = text
  
Output
- metadata of related sequences
- SVG file : occurrence plot of target+related species/strains on world map or specific area 

Components provided in this repo
1. Dockerfile or Singularity definition file
2. Related bash shell scripts
3. Related R scripts

Directory Scheme  
root
(
BMR.sif / BMR docker image);
;(DB/(
      existing species sequences:fasta (download before pipeline usage),
      existing species metedata:json (download before pipeline usage) 
      ) 
  )
;Scripts/ ()
