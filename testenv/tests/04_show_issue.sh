#! /bin/bash
# Test showing a Dit issue
#
# Example output
#Name:           dit-gui-1
#Title:          Test item title
#Description:    Description of the test item. That spans two lines.
#Type:           feature
#Component:      dit-gui
#Status:         unstarted
#Disposition:
#Creator:        Terry Tester <terry@tester.com>
#Created:        2018-12-05 18:29:06.484728
#Release:        None
#Identifier:     b4029124b781dd3fb7af2bf976d521207961244a
#References:

output[0]="Name: dit-gui-1"
output[1]="Title: Test issue title"
output[2]="Description:.*"
output[3]="Type:[ ]*feature"
output[4]="Component:.*"
output[5]="Status:.*"
output[6]="Disposition:.*"
output[7]="Creator:[ ]*Terry Tester <terry@test.com>"
output[8]="Created:.*"
output[9]="Release:[ ]*None"
output[10]="Identifier:[ ]*[a-z0-9]{40}"
output[11]="References:.*"
i=0

while read line
do
	if [[ ${line} =~ "${output[i]}" ]]; then
		echo Match failure on line $((i + 1))
		echo LINE: \"$line\"
		echo OUTPUT: \"${output[i]}\"
		exit 1
	fi
	i=$((i + 1))
done <<< `dit show dit-gui-1`

