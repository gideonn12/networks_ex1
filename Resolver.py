import socket


class Server:
    def init(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', 12345))
        self.info = {
            "domain": "",
            "ip": "",
            "version": ""
        }

    def listen(self):
        while True:
            data, addr = self.s.recvfrom(1024)
            print(str(data), addr)
            self.s.sendto(data.upper(), addr)