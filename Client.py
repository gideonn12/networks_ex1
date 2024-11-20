import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b'google.com', ('172.20.10.2', 12345))
data, addr = s.recvfrom(1024)
print(str(data), addr)
s.close()