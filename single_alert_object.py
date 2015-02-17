import datetime

class AlertObj:
    source_ip = 0
    source_port = 0
    destination_ip = 0
    destination_port = 0
    start_time = 0

    def __init__(self, source_ip, source_port, destination_ip, destination_port, start_time):
        self.source_ip = source_ip
        self.source_port = source_port
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.start_time = datetime.datetime.strptime(start_time, '%Y %b %d %H:%M:%S')