# -*- coding: utf-8 -*-
"""
Created on Fri May 31 16:56:13 2013

@author: proto
"""

try:
    from SimpleXMLRPCServer import SimpleXMLRPCServer  # nosec
except ImportError:
    from xmlrpc.server import SimpleXMLRPCServer  # nosec
try:
    from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler  # nosec
except ImportError:
    from xmlrpc.server import SimpleXMLRPCRequestHandler  # nosec
try:
    import defusedxml.xmlrpc
    defusedxml.xmlrpc.monkey_patch()
except ImportError:
    pass

import threading
import subprocess
import createGraph
import pexpect
try:
    import xmlrpclib  # nosec
except ImportError:
    import xmlrpc.client as xmlrpclib  # nosec
import glob
import os
# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server





class BipartiteServer:
    
    def __init__(self):
        pass
    def bipartite(self, bbnglFile,returnType,center,context,product):
        import tempfile
        import shutil
        import os
        print(center,context,product)
        bnglFile_data = bbnglFile.data
        temp_dir = tempfile.mkdtemp()
        try:
            bngl_path = os.path.join(temp_dir, 'temp.bngl')
            with open(bngl_path,'w') as f:
                f.write(bnglFile_data)
            self._bngl2xml(bngl_path)
            xml_path = os.path.join(temp_dir, 'temp.xml')
            createGraph.processBNGL(xml_path,center,context,product)
            dot_path = os.path.join(temp_dir, 'temp.xml.dot')
            with open(dot_path,'rb') as f:
                dot = f.read()
            png_path = os.path.join(temp_dir, 'temp.xml.png')
            with open(png_path,'rb') as f:
                png = f.read()
            if returnType == 'dot':
                data = xmlrpclib.Binary(dot)
            else:
                data = xmlrpclib.Binary(png)
            return data
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


    def getTransformations(self,bbnglFile):
        pass
    def _bngl2xml(self,bnglFile):
        subprocess.call(['bngdev', bnglFile, '--xml'], shell=False)
        
        


import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Start the Bipartite XML-RPC Server")
    parser.add_argument('--host', type=str, default=os.environ.get('HOST', '127.0.0.1'), help='Host IP address to bind to')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 9100)), help='Port to bind to')
    args = parser.parse_args()

    server = SimpleXMLRPCServer((args.host, args.port), requestHandler=RequestHandler)
    server.register_introspection_functions()
    server.register_instance(BipartiteServer())
    server.serve_forever()
