#! /bin/sh
# Calculate SLOC for all source in the repository
#

report_dir="$PWD/../reports/"
source_dir="$PWD/../dgui/"

[ ! -e "$report_dir" ] && mkdir -p $report_dir

sloccount --duplicates --wide --details $source_dir > $report_dir/sloccount.sc
