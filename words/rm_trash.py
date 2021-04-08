#/bin/python2
import hashlib 
import os
import random
import binascii
import datetime
import linecache
starttime = datetime.datetime.now()

def deltrash(trash):
    with open("onefile.txt","r") as file:
        for a,b in enumerate(file):
            if a in trash:
                print "PASSED line:"+str(a)
            else:
                with open("newOneFile.txt","a") as new:
                    new.write(b)

def ntlm_attack(filestring):
    errors = []
    input2 = raw_input("input hash to crack: ")

    with open(filestring) as file: # Use file to refer to the file object
        for i in enumerate(file):    
            w = i[1].rstrip("\n")
            try:
                passhash = hashlib.new('md4', w.encode('utf-16le')).digest()
                passhash = binascii.hexlify(passhash)
            except UnicodeDecodeError:
                print("unicode error found, a character probably isnt english: " + w)
                errors.append(i[0])

            if(str(passhash).upper() == input2.upper()):
                print("password found! Password is: " + w)
                file.close()
                break
        print "done"
    return errors
    file.close()
    endtime = datetime.datetime.now()
    timedifference = endtime-starttime;
    a = divmod(timedifference.days * 86400 + timedifference.seconds, 60)
    print str(a[0])+":"+str(a[1])
filepath = raw_input("Wordlist name and path: ")

trash = ntlm_attack(filepath)
deltrash(trash)
