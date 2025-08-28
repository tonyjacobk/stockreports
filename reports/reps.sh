#!/bin/bash
cd /home/ubuntu/stockreports/reports
# Get today's date in YYYY-MM-DD format
today_date=$(date +%Y-%m-%d)

# Define the target file
file_name="/tmp/myapp.log" # Replace 'F' with the actual file name

# Check if the file exists
if [[ ! -f "$file_name" ]]; then
  echo "Error: File '$file_name' not found."
  exit 1
fi

# Find and print lines containing today's date
grep "$today_date" "$file_name" |grep "Mail" > /tmp/maillog

python3 finalmail.py
cp /tmp/myapp.log /tmp/myapp.bak
python3 myftp.py
  
if [ $? -eq 0 ]; then
  echo "FTP done"
  rm /tmp/myapp.log
else
  echo "FTP failed"
fi


