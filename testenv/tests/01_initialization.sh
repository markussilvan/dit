#! /bin/bash
# Test Dit initialization

source testlib.inc

# remove existing output files, if any
rm -rf .dit-config bugs

# Initialize Dit, verify correct files were created
dit init >/dev/null << EOF
Terry Tester
terry@testcorp.com
bugs
EOF

assert_return_value "Dit initialization returned an error"
assert "-f .dit-config" "Dit config file not found"
assert "-d bugs" "Issue directory not found"

# Try to re-initialize
#dit init

#exit_on_error "Dit re-initialization returned an error"
#exit_if "[ ! -d issues ]" "Issue directory not found anymore"
#exit_if "[ ! -f .dit-config ]" "Dit config file not found anymore"
