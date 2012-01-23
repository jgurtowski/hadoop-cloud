
import os
import sys
import time
import StringIO
import re

from novaclient.v1_1 import client as nova_client

import multipart_writer


def getEnvVar(var):
    if not os.environ.has_key(var):
        msg = "Environment Var: %s not set, " % var
        msg += "did you source novarc?"
        raise Exception, msg
    return os.environ[var]


def getConnection():
    user = getEnvVar("NOVA_USERNAME")
    api_key = getEnvVar("NOVA_API_KEY")
    project = getEnvVar("NOVA_PROJECT_ID")
    nova_url = getEnvVar("NOVA_URL")

    return nova_client.Client(user,api_key,project,nova_url,insecure=True)

def waitForServer(client,server):
    i = 0
    sys.stdout.write("Waiting for %s to come up" % server.name)
    while True:
        sys.stdout.flush()
        if(client.servers.get(server.id).status == 'ACTIVE'):
            break
        elif(i == 18):
            raise Exception, "Timout: %s didn't come up" % server.name
        else:
            time.sleep(10)
        sys.stdout.write(".")
        i += 1
    print "Done"
    return client.servers.get(server.id)

class NamedStringIO(StringIO.StringIO):
    
    def setName(name):
        self.name = name


class Script:
        
    def __init__(self,name):
        self.sf_obj = NamedStringIO()
        self.addFileContents(name)
        self.sf_obj.name = name

    def addFileContents(self,filename):
        fh = open(filename)
        self.sf_obj.read()
        self.sf_obj.write(fh.read())
        fh.close()
        self.sf_obj.seek(0)
        self.sf_obj.name= filename

    def getFileLikeObject(self):
        return self.sf_obj

    def regexReplace(self,tag,value):
        self.sf_obj.seek(0)
        template = "<-%s->" % tag
        self.sf_obj.buf = re.sub(template,value,self.sf_obj.buf)
        
def main():
    
    if not len(sys.argv) == 6:
        sys.exit("%s num_nodes node_prefix config namenode key_name" % __file__)        
        
    num_nodes = int(sys.argv[1])
    node_prefix = sys.argv[2]
    config_file = sys.argv[3]
    namenode_name = sys.argv[4]
    keyname = sys.argv[5]

    nova = getConnection()

    image = nova.images.get("65") ###hardcode image and flavor
    flavor = nova.flavors.get("5") #xlarge

    node = Script("setup-hadoop.txt")
    node.addFileContents(config_file)
    node.regexReplace("namenode",namenode_name)
    node.regexReplace("jobtracker",namenode_name)
    node.regexReplace("cores",str(flavor.vcpus))
    node.regexReplace("mem", str(flavor.ram/flavor.vcpus))
    conf_files = [node.getFileLikeObject()]
    multipart_init  = multipart_writer.encodeFiles(conf_files)
    for i in range(num_nodes):
        node = nova.servers.create(node_prefix+str(i),
                                   image, flavor, key_name=keyname,
                                   userdata=multipart_init)
        multipart_init.seek(0)
        
        
if __name__ == "__main__":
    main()





