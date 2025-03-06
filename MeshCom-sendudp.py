import socket

def send_udp_message (message, ip_address, port):
  try:
    # Create an UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send a Message
    sock.sendto(message.encode(), (ip_address,port))

    # Close the socket
    sock.close()

    return True
  except Exception as e:
    print(f"Error: {e}")
    return False

  #Direkt Nachricht
  #message = {"type":"msg","dst":"DK5EN-99","msg":"Test direkt an DK5EN-99 via UDP"}

  #Broadcast Nachricht
  #message = {"type":"msg","dst":"999","msg":"Test auf die 999 via UDP"}
  #message = "{\"type\":\"msg\",\"dst\":\"DK5EN-99\",\"msg\":\"Test direkt an DK5EN-99 via UDP\"}"

#grp="999"
#grp="DK5EN-99"
grp="*"

#Standard Text an MeshCom
msg="Test auf die " + grp + " via UDP + DNS Auflösung zusammengesetzt"

#Standard Text an APRS.fi
#msg="APRS:Test auf die " + grp + " via UDP + DNS Auflösung zusammengesetzt"
#msg="APRS: mal alles raus an aprsi.fi "

#src_type = node
#{"src_type":"node","type":"pos","src":"DK5EN-99","msg":"","lat":48.4073,"lat_dir":"N","long":11.7412,"long_dir":"E","aprs_symbol":"G","aprs_symbol_group":"/","hw_id":"3","msg_id":"7AD58135","alt":1640,"batt":100}


#src_type = lora
#{ "src_type":"lora","type":"pos","src":"DL3NCU-1,DB0ED-1","msg":"","lat":48.3015,"lat_dir":"N","long":11.9145,"long_dir":"E","aprs_symbol":"#","aprs_symbol_group":"/","hw_id":"3","msg_id":"1F32F00F","alt":1677,"batt":100,"firmware":"4.34"}

# {"src_type":"lora","type":"pos","src":"DG7RJ-1,DG7RJ-12,DK5EN-12","msg":"","lat":48.3017,"lat_dir":"N","long":11.6278,"long_dir":"E","aprs_symbol":"b","aprs_symbol_group":"/","hw_id":"12","msg_id":"39D1309B","alt":1545,"batt":100,"firmware":"4.34"}
#{"src_type":"lora","type":"pos","src":"DG7RJ-3,DG7RJ-12,DK5EN-12","msg":"","lat":48.3022,"lat_dir":"N","long":11.6277,"long_dir":"E","aprs_symbol":"#","aprs_symbol_group":"/","hw_id":"43","msg_id":"EA0A8095","alt":1526,"batt":100,"firmware":"4.34"}

#{"src_type":"lora","type":"pos","src":"DL2JA-1","msg":"","lat":48.4230,"lat_dir":"N","long":11.7865,"long_dir":"E","aprs_symbol":"-","aprs_symbol_group":"/","hw_id":"43","msg_id":"E9F1106F","alt":1785,"batt":100,"firmware":"4.34"}

#{"src_type":"lora","type":"pos","src":"DB0ED-1,DL2JA-1","msg":"","lat":48.2860,"lat_dir":"N","long":12.0337,"long_dir":"E","aprs_symbol":"#","aprs_symbol_group":"/","hw_id":"43","msg_id":"4F747195","alt":1726,"batt":100,"firmware":"4.34"}

#{"src_type":"udp","type":"msg","src":"OE1XAR-45","dst":"*","msg":"{CET}2025-03-04 11:21:14","msg_id":"67C45485"}
#{"src_type":"udp","type":"msg","src":"OK2ZAW-43","dst":"*","msg":"rak test","msg_id":"B4FB7003"}
#{"src_type":"udp","type":"msg","src":"OE1XAR-45","dst":"*","msg":"{CET}2025-03-04 11:36:18","msg_id":"67C45488"}

#{"src_type":"lora","type":"pos","src":"DG7RJ-12,DK5EN-12","msg":"","lat":48.3022,"lat_dir":"N","long":11.6277,"long_dir":"E","aprs_symbol":"-","aprs_symbol_group":"/","hw_id":"43","msg_id":"EF2ED257","alt":1526,"batt":100,"firmware":"4.34"}
#{"src_type":"lora","type":"pos","src":"DK5EN-12","msg":"","lat":48.4077,"lat_dir":"N","long":11.7385,"long_dir":"E","aprs_symbol":"G","aprs_symbol_group":"/","hw_id":"43","msg_id":"EFF8503C","alt":1585,"batt":100,"firmware":"4.34"}


message = "{\"type\":\"msg\",\"dst\":\"" + grp + "\",\"msg\":\"" + msg + "\"}"


print(f"Message : {message}")
port = 1799 #	 stadard Port für MC

hostname = "dk5en-99.local"
ip_address = socket.gethostbyname(hostname)

#debug code
#print("IP-Adresse von {} ist {}".format(hostname, ip_address))

if send_udp_message(message,ip_address,port):
    print("Message sent sccessful!")
else:
    print("Failed to send message.")
