import socket
import sys


class Resolver:
    def __init__(self, myPort, parentIP, parentPort, x):
        self.cache = {}
        self.parentIP = parentIP
        self.parentPort = parentPort
        self.cache_timeout = x
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', myPort))

    def send_and_return(self, ip, port, query):
        print("Sending query", query, "to", ip, "on port", port)
        self.s.sendto(query.encode(), (ip, int(port)))
        data, addr = self.s.recvfrom(1024)
        print("Received response:", data.decode())
        return data.decode()

    def search_cache(self, query):
        # filter the query to domain, IP and version, they are separated by a ","
        if query == "non-existent domain":
            return query
        
        if "," in query:
            domain, ip, version = query.split(",")
            if version == "A":
                self.cache[domain] = query
                return query
            if version == "NS":
                ip, port = ip.split(":")
                query = self.send_and_return(ip, port, domain)
                if query == "non-existent domain":
                    return query
                temp, ip, version = query.split(",")
                return self.search_cache(domain+","+ip+":"+port+","+version)
        else:
            domain = query

        if domain in self.cache:
            return self.cache[domain]
        # assume by convention that the ending of a domain starts with a '.'
        ending = '.'+'.'.join(domain.split('.', 1)[1:])
        # TODO: fix this
        if ending in self.cache:
            # TODO: send to the right IP and port
            res = self.send_and_return(ip, port, query)
            # filter again to get the domain, IP and version
            # TODO: check again for "google.com" or long query
            domain, ip, version = res.split(",")
            if version == "A":
                self.cache[domain] = res
                return res
            if res == "non-existent domain":
                return res
            else:
                self.cache[domain] = res
                ip, port = ip.split(":")
                self.search_cache(ip, port, res)
        else:
            # if the domain is not in the cache, send the query to the parent
            res = self.send_and_return(self.parentIP, self.parentPort, query)
            if res == "non-existent domain":
                return res
            # no way to return just google.com
            
            temp, ip, version = res.split(",")
            if version == "A":
                self.cache[domain] = res
                return res
            if version == "NS":
                self.cache[domain] = res
            return self.search_cache(domain+","+ip+","+version)
            

    def listen(self):
        while True:
            data, addr = self.s.recvfrom(1024)
            query = data.decode()
            print("Received query:", query)
            res = self.search_cache(query)
            print("response:", res)
            self.s.sendto(res.encode(), addr)


if __name__ == "__main__":
    myPort = int(sys.argv[1])
    parentIP = sys.argv[2]
    parentPort = int(sys.argv[3])
    x = int(sys.argv[4])

    resolver = Resolver(myPort, parentIP, parentPort, x)
    resolver.listen()

# import time

# def search_cache(self, query, timeout):
#     # filter the query to domain, IP and version, they are separated by a ","
#     domain, ip, version = query.split(",")
#     if version == "NA":
#         ip, port = ip.split(":")

#     current_time = time.time()

#     if domain in self.cache:
#         value, timestamp = self.cache[domain]
#         if current_time - timestamp < timeout:
#             return value
#         else:
#             del self.cache[domain]  # Remove expired record

#     # assume by convention that the ending of a domain starts with a '.'
#     ending = '.'.join(domain.split('.', 1)[1:])
#     if ending in self.cache:
#         value, timestamp = self.cache[ending]
#         if current_time - timestamp < timeout:
#             return value
#         else:
#             del self.cache[ending]  # Remove expired record

#     res = self.send_and_return(ip, port, query)
#     # filter again to get the domain, IP and version
#     self.cache[domain] = (res, current_time)  # Store the result with the current timestamp
#     return res
