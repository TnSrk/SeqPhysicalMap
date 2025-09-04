jq -r '.[] | select(has("country") and (.country | test("'$1'"; "i"))) | [.country,.Id,.strain,(.CollectionDate // .CreateDate // "NA")] | @tsv'
