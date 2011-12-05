
import os
import sys
import time

from novaclient.v1_1 import client as nova_client


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

    return nova_client.Client(user,api_key,project,nova_url)

def waitForServer(client,server):
    i = 0
    sys.stdout.write("Waiting for %s to come up" % server.name)
    while True:
        sys.stdout.flush()
        if(client.servers.get(server.id).status == 'ACTIVE'):
            break
        elif(i == 6):
            raise Exception, "Timout: %s didn't come up" % server.name
        else:
            time.sleep(10)
        sys.stdout.write(".")
        i += 1
    print "Done"
    return client.servers.get(server.id)

def main():
    
    if not len(sys.argv) == 3:
        sys.exit("%s num_datanodes node_prefix" % __file__)        

    num_datanodes = int(sys.argv[1])
    if num_datanodes < 1 or num_datanodes > 200:
        sys.exit("1<=num_datanodes<=200")

    node_prefix = sys.argv[2]

    nova = getConnection()

    image = nova.images.get("37") ###hardcode image and flavor
    flavor = nova.flavors.get("3") #medium

    namenode = nova.servers.create(node_prefix+"_hdp_namenode",
                                   image, flavor)

    namenode = waitForServer(nova,namenode)
    
    namenode_ip =  namenode.addresses['private'][0]
    
if __name__ == "__main__":
    main()





