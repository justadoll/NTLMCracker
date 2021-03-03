#!/bin/bash
#hashcat -a 3 -m 0 sss.hash /usr/share/wordlists/rock_500.txt -O -o cracked.txt --potfile-disable

hashcat --force --hwmon-temp-abort=100 -m 1000 -D 1,2 -a 3 $1 /usr/share/wordlists/rockyou.txt -O -o $2
hashcat --force --hwmon-temp-abort=100 -m 1000 -D 1,2 -a 3 $1 /usr/share/wordlists/rockyou.txt -O -o $2 --show
