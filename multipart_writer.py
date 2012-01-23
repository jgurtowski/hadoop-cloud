# largely taken from python examples
# http://docs.python.org/library/email-examples.html

import os
import sys
import StringIO

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gzip

starts_with_mappings={
    '#include' : 'text/x-include-url',
    '#!' : 'text/x-shellscript',
    '#cloud-config' : 'text/cloud-config',
    '#upstart-job'  : 'text/upstart-job',
    '#part-handler' : 'text/part-handler',
    '#cloud-boothook' : 'text/cloud-boothook'
}

def get_type(f):
    line = f.readline()
    
    rtype = "text/plain"
    for beg,mtype in starts_with_mappings.items():
        if line.startswith(beg):
            rtype = mtype
            break
    f.seek(0)
    return(rtype)

def encodeFiles(filelist):

    outer = MIMEMultipart()
    for fileobj in filelist:
        mtype = get_type(fileobj)
        maintype, subtype = mtype.split('/', 1)
        if maintype == 'text':
            msg = MIMEText(fileobj.read(), _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fileobj.read())
            # Encode the payload using Base64
            encoders.encode_base64(msg)
        fileobj.seek(0)
        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment',
                       filename=fileobj.name)

        outer.attach(msg)
    
    outputFile = StringIO.StringIO()
    gfile = gzip.GzipFile(fileobj=outputFile, 
                          mode="w",
                          filename="multipart-config.txt" )
    gfile.write(outer.as_string())
    gfile.close()
    
    outputFile.seek(0)
    return outputFile
