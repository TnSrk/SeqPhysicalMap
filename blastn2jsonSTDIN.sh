#!/bin/bash

# Read from stdin, normalize line endings, and remove trailing/leading whitespace
# Pipe directly to awk
cat - | tr -d '\r' | sed 's/^[ \t]*//;s/[ \t]*$//' | awk '
BEGIN {
    print "[" # Start JSON array
    first_record = 1
    block = ""
    block_lines = 0
}

{
    # Trim line (already trimmed by sed, but ensure consistency)
    line = $0

    # Accumulate lines into block
    if (block_lines > 0) {
        block = block (block == "" ? "" : "\n") line
        block_lines++
    } else {
        block = line
        block_lines = 1
    }

    # Check if line contains <SubName>
    if (line ~ /<SubName>/) {
        # Process block
        id = ""
        title = ""
        extra = ""
        createdate = ""
        subtypes = ""
        subnames = ""

        # Split block into lines
        split(block, lines, "\n")
        for (i = 1; i <= block_lines; i++) {
            # Extract 12-column line for Id (first line)
            if (i == 1 && lines[i] !~ /^</) {
                split(lines[i], fields, /[ \t]+/)
                if (length(fields) == 12) {
                    id = fields[2] "_" fields[9]
                }
            }
            # Extract tagged fields
            if (lines[i] ~ /^<Title>/) {
                sub(/^<Title>/, "", lines[i])
                sub(/<\/Title>$/, "", lines[i])
                title = lines[i]
            }
            if (lines[i] ~ /^<Extra>/) {
                sub(/^<Extra>/, "", lines[i])
                sub(/<\/Extra>$/, "", lines[i])
                extra = lines[i]
            }
            if (lines[i] ~ /^<CreateDate>/) {
                sub(/^<CreateDate>/, "", lines[i])
                sub(/<\/CreateDate>$/, "", lines[i])
                createdate = lines[i]
            }
            if (lines[i] ~ /^<SubType>/) {
                sub(/^<SubType>/, "", lines[i])
                sub(/<\/SubType>$/, "", lines[i])
                subtypes = lines[i]
            }
            if (lines[i] ~ /^<SubName>/) {
                sub(/^<SubName>/, "", lines[i])
                sub(/<\/SubName>$/, "", lines[i])
                subnames = lines[i]
            }
        }

        # Skip invalid blocks (no Id)
        if (id == "") {
            print "DEBUG: Skipping block due to missing Id: " block > "/dev/stderr"
            block = ""
            block_lines = 0
            next
        }

        # Start JSON object
        if (first_record) {
            first_record = 0
        } else {
            print ","
        }
        print "  {"
        printf "    \"Id\": \"%s\",\n", id

        # Output tagged fields
        printf "    \"Title\": \"%s\",\n", title ? title : "N/A"
        printf "    \"Extra\": \"%s\",\n", extra ? extra : "N/A"
        printf "    \"CreateDate\": \"%s\"", createdate ? createdate : "N/A"

        # Process SubType and SubName
        if (subtypes != "" && subnames != "") {
            split(subtypes, subtype_array, "|")
            split(subnames, subname_array, "|")
            for (j = 1; j <= length(subtype_array); j++) {
                if (j <= length(subname_array)) {
                    print ","
                    printf "    \"%s\": \"%s\"", subtype_array[j], subname_array[j] ? subname_array[j] : "N/A"
                }
            }
        }

        print "\n  }"

        # Reset block
        block = ""
        block_lines = 0
    }
}

END {
    print "]"
}
' | sed ':a;s/\([^\\]\)"/\1\\"/g;ta' 
