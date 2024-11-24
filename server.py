import socket
import sys


class Server:
    def __init__(self, port, zone):
        self.list = []
        self.info = {
            "domain": "",
            "ip": "",
            "version": ""
        }
        self.zone = zone
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', port))

    def print_list(self):
        for i in self.list:
            print(f"{i['domain']},{i['ip']},{i['version']}")

    def load_file(self):
        with open(self.zone, "r") as f:
            for line in f:
                domain, ip, version = line.split(",")
                self.list.append({
                    "domain": domain,
                    "ip": ip,
                    "version": version.strip()})

    def search_in_list(self, domain):
        # case 1: domain is in list
        for i in self.list:
            if i["domain"] == domain:
                return i
        # case 2: check for subdomains in list
        for i in self.list:
            if domain.endswith(i["domain"]):
                return i
        # case 3: domain is not in list
        else:
            return "non-existent domain"

    def listen(self):
        while True:
            data, addr = self.s.recvfrom(1024)
            domain = data.decode()
            print(domain)
            ans = self.search_in_list(domain)
            if isinstance(ans, dict):
                ans = f"{ans['domain']},{ans['ip']},{ans['version']}"
            print(ans)
            self.s.sendto(ans.encode(), addr)


if __name__ == '__main__':
    arg1 = int(sys.argv[1])
    arg2 = sys.argv[2]
    s = Server(arg1, arg2)
    s.load_file()
    s.listen()
