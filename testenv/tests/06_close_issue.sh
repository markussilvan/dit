#! /bin/bash
# Test starting work on a Dit issue
#

expect <<EOF
spawn dit close dit-gui-1
expect "Disposition:"
send -- "\r"
expect "Comment:"
send -- "Hey, I have finished work on this issue!\r"
send -- "/stop\r"
expect eof
EOF

status=`grep Status bugs/issue-*`
echo $status
