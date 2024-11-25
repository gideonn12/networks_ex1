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
        self.s.sendto(query.encode(), (ip, int(port)))
        data, addr = self.s.recvfrom(1024)
        return data.decode()

    def save_to_cache(self, domain, query):
        # add the query to the cache with the domain as the key
        self.cache[domain] = {"query": query, "time": datetime.now()}

    def handle_direct_cache(self, query):
        # handle the case where the query is in the cache
        # clear the cache of expired entries
        self.clear_cache()
        if query in self.cache:
            return self.cache[query].get("query")
        return None

    def resolve_subdomain(self, domain):
        # handle the case where the query is a subdomain
        ending = domain[1:]
        self.clear_cache()
        while ending:
            # clear the cache of expired entries
            if ending in self.cache:
                # if the version is A, it's irrelevant, and need to continue searching
                if self.cache[ending].get("query").split(",")[2] == "A":
                    ending = ending[1:]
                    continue
                return self.cache[ending].get("query")
            ending = ending[1:]
        return None

    def handle_version_A(self, domain, query):
        # handle the case where the query is of version A
        self.save_to_cache(domain, query)
        return query

    def handle_version_NS(self, query, ip, port, original_query):
        # handle the case where the query is of version NS
        domain, ip, version = query.split(",")
        ip, port = ip.split(":")
        self.save_to_cache(domain, query)
        return self.send_and_return(ip, port, original_query)

    def parse_query(self, query):
        if "," in query:
            return query.split(",")
        return query, None, None

    def clear_cache(self):
        # clear the cache of expired entries
        current_time = datetime.now()
        lst = []
        for domain, data in self.cache.items():
            if (current_time - data.get("time")).seconds > self.cache_timeout:
                lst.append(domain)
        for domain in lst:
            del self.cache[domain]

    def search_cache(self, query):
        # Step 1: Handle non-existent domain
        if query == "non-existent domain":
            return query

        # Step 2: Parse the query
        domain, ip, version = self.parse_query(query)

        if version == "A":
            return self.handle_version_A(domain, query)
        if version == "NS":
            ip, port = ip.split(":")
            data = self.handle_version_NS(query, ip, port, domain)
            return self.search_cache(data)

        # Step 3: Check for direct match in cache
        direct_match = self.handle_direct_cache(domain)
        if direct_match:
            print("Direct match found in cache")
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
        if version == "NS":
            ip, port = ip.split(":")
            data = self.handle_version_NS(query, ip, port, domain)
            return self.search_cache(data)

        # Step 5: Query the parent resolver
        response = self.send_and_return(self.parentIP, self.parentPort, query)
        if response == "non-existent domain":
            # first save the query in the cache
            self.save_to_cache(domain, response)
            return response
        temp, ip, version = response.split(",")
        if version == "A":
            return self.handle_version_A(domain, response)
        if version == "NS":
            ip, port = ip.split(":")
            data = self.handle_version_NS(response, ip, port, domain)
            return self.search_cache(data)

    def listen(self):
        while True:
            data, addr = self.s.recvfrom(1024)
            query = data.decode()
            res = self.search_cache(query)
            self.s.sendto(res.encode(), addr)


if __name__ == "__main__":
    myPort = int(sys.argv[1])
    parentIP = sys.argv[2]
    parentPort = int(sys.argv[3])
    x = float(sys.argv[4])

    resolver = Resolver(myPort, parentIP, parentPort, x)
    resolver.listen()
