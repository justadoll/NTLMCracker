#!/bin/bash
#hashcat -a 3 -m 0 sss.hash /usr/share/wordlists/rock_500.txt -O -o cracked.txt --potfile-disable
#cat cracked.txt

#cat: cracked.txt: No such file or directory return false
echo -n "Insert hash pls: "
read VAR
hashcat --force --hwmon-temp-abort=100 -m 1000 -D 1,2 -a 3 $VAR /usr/share/wordlists/rockyou.txt -O -o test123.txt
hashcat --force --hwmon-temp-abort=100 -m 1000 -D 1,2 -a 3 $VAR /usr/share/wordlists/rockyou.txt -O -o test.txt --show
cat test.txt
#a2345375a47a92754e2505132aca194b
