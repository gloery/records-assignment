import sys
import re
from datetime import date, datetime

import xmlrpclib

from single_alert_object import AlertObj

# these are the values that will be given to ip addresses and ports, respectively, if no other value is specified in a record
DEFAULT_IP_ADDRESS = 0
DEFAULT_PORT_NUMBER = 0


def parse_file(filename):
    """Take in an ASCII file name and for each line in that file, extract the timestamp, source ip address, source port number, destination ip address,
    and destination port number. There is only guaranteed to be a timestamp and source ip address. All other fields default to 0 (or 0.0.0.0 in the case of an ip address)
    if no value is provided in the line of the file. Combines all those attributes as properties into one object, called an AlertObj. This process is repeated for each line in the file
    and eventually a list is returned, containing one alert object for each line in the file.

    Keyword arguments:
    filename -- the name of the ASCII file to extract values from
    """
    alert_obj_list = []

    with open(filename) as f:
        # group(1) is the pattern for the timestamp, group 2 is the pattern for the source ip address, group 3 is the pattern for the source port number
        # group(4) is the pattern for the destination ip address (if one exists), and group(5) is the pattern for the destination port number (if one exists)
        pattern = '([A-Z][a-z]{2} [0-9]+? [0-9]{2}:[0-9]{2}:[0-9]{2}).*?([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+):?([0-9]+)?(?: -> )?([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)?:?([0-9]+)?'
        # since we're going to be using the same pattern over and over on many lines, it makes sense to compile it here

        # reading line-by-line is much more efficient in space and time for large datasets than reading in everything at once
        prog = re.compile(pattern)
        for line in f:
            # use groups to efficiently get all things in one regex pass
            m = prog.match(line)
            # this gets the current year and appends it onto the timestamp provided in the record
            timestamp = str(date.today().year)+ ' '+m.group(1)
            source_ip = ip_to_int(m.group(2))
            # ip addresses need to be converted to ints
            if m.group(3) == None:
                source_port = DEFAULT_PORT_NUMBER
            else:
                source_port = int(m.group(3))
            if m.group(4) == None:
                destination_ip = DEFAULT_IP_ADDRESS
            else:
                destination_ip = ip_to_int(m.group(4))
            if m.group(5) == None:
                destination_port = DEFAULT_PORT_NUMBER
            else:
                destination_port = int(m.group(5))
            # create an object with all the captured groups as properties of that object
            alert_obj = AlertObj(source_ip, source_port, destination_ip, destination_port, timestamp)
            alert_obj_list.append(alert_obj)
    return alert_obj_list


def process_alert(record_object, server):
    """Send a record object to an XML RPC server.

    Keyword arguments:
    record_object -- an object that corresponds to a line parsed in the previous method, with each record object having five attributes:
    its start time (e.g. timestamp), its source ip address, its source port number (or 0 if none was provided), its destination ip address (or 0.0.0.0 if none given)
    and its destination port number (again, 0, if none was provided).
    server -- the name and port number of the XML RPC the user wants to contact (in the format 'server_name:port_number') 
    """
    start_time = record_object.start_time
    ip_port_pair = [record_object.source_ip, record_object.source_port, record_object.destination_ip, record_object.destination_port]

    # Not strictly necessary given the scope of the assignment. However, this provides a hack-y but reliable way to allow for long ints to be returned as output from the server
    # by changing the <int> tag to <i8>. However, this is NOT officially supported by the XML RPC specification, so should be used with caution.
    # credit for workaround: jhermann at http://stackoverflow.com/questions/18533309/xmlrpc-response-datatype-long-possible
    xmlrpclib.Marshaller.dispatch[type(0L)] = lambda _, v, w: w("<value><i8>%d</i8></value>" % v)
    
    # datetime objects can be passed in by default as parameters to server functions; however, setting use_datetime to True anyway to keep formatting consistent for input/output
    server = xmlrpclib.ServerProxy('http://' + server, use_datetime = True)
    return server.process_alert(start_time, ip_port_pair)

def ip_to_int(ip_address):
    """Convert an ip address to an integer

    Keyword arguments:
    ip_address -- the ip address to be converted
    """
    pattern = '([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)'
    m = re.search(pattern, ip_address)
    first_octet = int(m.group(1))
    second_octet = int(m.group(2))
    third_octet = int(m.group(3))
    fourth_octet = int(m.group(4))

    int_address = first_octet*(256**3) + second_octet*(256**2) + third_octet*(256) + fourth_octet

    return int_address
def int_to_ip(input_int):
    """Convert an integer to an ip address. Not strictly necessary for this problem as defined, but it would probably come in handy for
    doing data analysis later on.
    """
    full_address = ""
    first_group = int(input_int / (256**3)) % 256
    second_group = int(input_int / (256**2)) % 256
    third_group = int(input_int / 256) % 256
    fourth_group = int(input_int) % 256
    
    full_address = str(first_group) + '.' + str(second_group) + '.' + str(third_group) + '.' + str(fourth_group)
    return full_address

def main():
    if len(sys.argv) == 3:
        filename = sys.argv[1]
        server = sys.argv[2]
    else:
        print 'Error: input should be of the format "python SendRecordsToServer.py <record file> <server host:port>"'
        return
    alert_obj_list = parse_file(filename)

    for alert_obj in alert_obj_list:
        print(process_alert(alert_obj, server))

#Only run main() if this is being run as a script 
if __name__ == '__main__':
    main()