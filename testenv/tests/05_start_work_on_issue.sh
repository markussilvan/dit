#! /bin/bash
# Test starting work on a Dit issue
#

expect <<EOF
spawn dit start dit-gui-1
expect "Comment:"
send -- "Hey, I am starting work on this issue!\r"
send -- "/stop\r"
expect eof
EOF

status=`grep Status bugs/issue-*`
echo $status
