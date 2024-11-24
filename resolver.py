from datetime import datetime
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

    def save_to_cache(self, domain, query):
        # add the query to the cache with the domain as the key
        self.cache[domain] = {"query": query, "time": datetime.now()}
        print("Saved to cache:", domain, query)

    def handle_direct_cache(self, query):
        # handle the case where the query is in the cache
        if query in self.cache:
            return self.cache[query].get("query")
        return None

    def resolve_subdomain(self, domain):
        # handle the case where the query is a subdomain
        ending = domain[1:]
        while ending:
            if ending in self.cache:
                return self.cache[ending].get("query")
            ending = ending[1:]
        return None

    def handle_version_A(self, domain, query):
        # handle the case where the query is of version A
        self.save_to_cache(domain, query)
        return query

    def handle_version_NS(self, query, ip, port):
        # handle the case where the query is of version NS
        domain, ip, version = query.split(",")
        ip, port = ip.split(":")
        self.save_to_cache(domain, query)
        return self.send_and_return(ip, port, domain)

    def parse_query(self, query):
        if "," in query:
            return query.split(",")
        return query, None, None

    def search_cache(self, query):
        # Step 1: Handle non-existent domain, TODO: need to save in cache
        if query == "non-existent domain":
            return query
        
        # Step 2: Parse the query
        domain, ip, version = self.parse_query(query)
        
        if version == "A":
            return self.handle_version_A(domain, query)
        if version == "NS":
            ip, port = ip.split(":")
            data = self.handle_version_NS(query, ip, port)
            return self.search_cache(data)

        # Step 3: Check for direct match in cache
        direct_match = self.handle_direct_cache(domain)
        if direct_match:
            return direct_match

        # Step 4: Handle subdomain cache resolution
        subdomain_result = self.resolve_subdomain(domain)
        if subdomain_result:
            # filter the query to domain, IP and version, they are separated by a ","
            domain, ip, version = subdomain_result.split(",")
            ip, port = ip.split(":")
            data = self.send_and_return(ip, port, domain)
            return self.search_cache(data)

        # Step 6: Process response based on version
        if version == "A":
            return self.handle_version_A(domain, query)
            print("please stop1")
        if version == "NS":
            ip, port = ip.split(":")
            date = self.handle_version_NS(query, ip, port)
            return self.search_cache(data)

        # Step 5: Query the parent resolver
        response = self.send_and_return(self.parentIP, self.parentPort, query)
        if response == "non-existent domain":
            return response
        temp, ip, version = response.split(",")
        if version == "A":
            return self.handle_version_A(domain, response)
            print("please stop2")
        if version == "NS":
            ip, port = ip.split(":")
            data = self.handle_version_NS(response, ip, port)
            return self.search_cache(data)

    def listen(self):
        while True:
            data, addr = self.s.recvfrom(1024)
            query = data.decode()
            print("Received query:", query)
            res = self.search_cache(query)
            print("response:", res)
            self.s.sendto(res.encode(), addr)

        # filter the query to domain, IP and version, they are separated by a ","
        if query == "non-existent domain":
            return query

        if "," in query:
            domain, ip, version = query.split(",")
            if version == "A":
                # TODO: change in code to match query field in cache dict
                self.cache[domain] = {"query": query, "time": datetime.now()}
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
            return self.cache[domain].get("query")
        # assume by convention that the ending of a domain starts with a '.'
        ending = domain[1:]

        if ending in self.cache:
            domain_to_send = self.cache[ending].get("query").split(":")
            res = self.send_and_return(
                domain_to_send[0], domain_to_send[1], domain)
        else:
            # if the domain is not in the cache, send the query to the parent
            res = self.send_and_return(self.parentIP, self.parentPort, query)
        if res == "non-existent domain":
            return res
        # no way to return just google.com

        temp, ip, version = res.split(",")
        if version == "A":
            # TODO: change in code to match query field in cache dict
            self.cache[domain] = res
            return res
        if version == "NS":
            # TODO: change in code to match query field in cache dict
            self.cache[domain] = res
        return self.search_cache(domain+","+ip+","+version)


if __name__ == "__main__":
    myPort = 12345
    parentIP = "172.20.10.3"
    parentPort = 7777
    x = 60
    
    

    # myPort = int(sys.argv[1])
    # parentIP = sys.argv[2]
    # parentPort = int(sys.argv[3])
    # x = float(sys.argv[4])

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
