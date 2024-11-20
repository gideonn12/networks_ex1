import socket
import sys


class Resolver:
    def __init__(self, myPort, parentIP, parentPort, x):
        # print all the arguments
        print("myPort: ", myPort, "parentIP: ", parentIP,
              "parentPort: ", parentPort, "x: ", x)
        self.cache = {}
        self.parentIP = parentIP
        self.parentPort = parentPort
        self.cache_timeout = x
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', myPort))

    def send_and_return(self, ip, port, query):
        self.s.sendto(query.encode(), (ip, port))
        data, addr = self.s.recvfrom(1024)
        return data.decode()

    def search_cache(self, query):
        # filter the query to domain, IP and version, they are separated by a ","
        domain, ip, version = query.split(",")
        if version == "NA":
            ip, port = ip.split(":")
        if domain in self.cache:
            return self.cache[domain]
        # assume by convention that the ending of a domain starts with a '.'
        ending = '.'.join(domain.split('.', 1)[1:])
        if ending in self.cache:

            res = self.send_and_return(ip, port, query)
            # filter again to get the domain, IP and version
            domain, ip, version = res.split(",")
            if version == "A":
                self.cache[domain] = res
                return res
            if res == "Non-existent":
                return res
            else:
                self.cache[domain] = res
                ip, port = ip.split(":")
                self.search_cache(ip, port, res)

        else:
            # if the domain is not in the cache, send the query to the parent
            res = self.send_and_return(self.parentIP, self.parentPort, query)

    def listen(self):
        while True:
            data, addr = self.s.recvfrom(1024)
            query = data.decode()
            print("Received query: ", query)
            print("Searching cache for query: ", query)
            # res = self.search_cache(query)
        
            


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
