import send_records_to_server as prog

alerts = prog.parse_file('input.txt')
for alert in alerts:
    result = prog.process_alert(alert, 'localhost:8000')
    print result