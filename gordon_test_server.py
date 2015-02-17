from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
class GordonXMLRPCServer:
    def process_alert(start_time, ip_port_pair):
        strings_to_return = []
        strings_to_return.append(start_time)
        # strings_to_return.append(ip_port_pair)
        return strings_to_return
        
    server = SimpleXMLRPCServer(("localhost", 8000),
                            requestHandler=RequestHandler)
    server.register_function(process_alert)
    server.serve_forever()