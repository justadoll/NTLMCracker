import hashlib 
import os
import random
import binascii
import datetime
#async?
#taskbar? 1/10 ?

def crack_ntlm(str_hash:str,dictio:str):
    with open(dictio) as file:
        for i in enumerate(file):
            i = i[1].rstrip("\n")
            try:
                passhash = hashlib.new('md4', i.encode('utf-16le')).digest()
                passhash = binascii.hexlify(passhash)
            except UnicodeDecodeError:
                print('unicodeError')
            if(str(passhash.decode('ascii')).upper() == str_hash.upper()):
                return i
                #print(f"Password:{i}")
                break

#print(crack_ntlm("A10705E348EFCCF3D369A4FFC83DD88E","words/newOneFile.txt"))
