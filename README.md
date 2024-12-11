# networks_ex1

# Digital 144 Service Simulation
Overview

This project simulates a digital 144-style service. The goal is to implement a UDP server that can respond to queries about domain-to-IP mappings. Unlike the traditional 144 telephone service (which maps names to phone numbers), this service maps domain names to IP addresses.

The project includes three components:

Authoritative Server: Loads a zone.txt file containing domain-to-IP mappings and responds to queries based on it.
Resolver Server: Acts as a DNS resolver, forwarding queries to a parent authoritative server, caching responses, and serving subsequent queries from the cache for a specified time.
Client: Sends domain queries to the resolver server and displays the IP address or an error message.

Components
Authoritative Server

Functionality:
        Loads mappings from a zone.txt file at startup. Each line in the file represents a mapping in the format:
        <domain>,<IP or IP:port>,<type>
        Example:

    biu.ac.il,1.2.3.4,A
    .co.il,1.2.3.5:777,NS
    example.com,1.2.3.7,A

    Responds to queries by matching domains with the file's records.
        If a direct match of type A exists, it returns the corresponding IP address.
        If no direct match exists, but a matching NS record is found (e.g., for subdomains), it returns the nameserver details.
        If no match exists, it responds with non-existent domain.

Usage:

    server.py [myPort] [zoneFileName]

    Arguments:
        myPort: Port for the server to bind and listen on.
        zoneFileName: Path to the zone.txt file containing domain mappings.

Resolver Server

Functionality:
        Forwards queries to a parent authoritative server if the requested domain is not in its cache.
        Caches responses for x seconds, after which cached entries expire.
        Handles chains of nameserver referrals to resolve domains fully.

    Usage:

    resolver.py [myPort] [parentIP] [parentPort] [x]

    Arguments:
        myPort: Port for the resolver server to bind and listen on.
        parentIP: IP address of the parent authoritative server.
        parentPort: Port of the parent authoritative server.
        x: Time (in seconds) for which cached entries remain valid.

Client

Functionality:
        Sends domain queries to the resolver server and displays the corresponding IP address (or error message) received.

    Usage:

    client.py [serverIP] [serverPort]

    Arguments:
        serverIP: IP address of the resolver server.
        serverPort: Port of the resolver server.

Example Usage
Files

zone.txt:

biu.ac.il,1.2.3.4,A
.co.il,1.2.3.5:777,NS
example.com,1.2.3.7,A

zone2.txt:

www.google.co.il,1.2.3.8,A
mail.google.co.il,1.2.3.9,A

Steps

    Start the authoritative servers:

server.py 55555 zone.txt
server.py 777 zone2.txt

Start the resolver server:

resolver.py 12345 127.0.0.1 55555 60

Start the client:

client.py 127.0.0.1 12345

Client interaction example:

    Input: biu.ac.il
    Output: 1.2.3.4

    Input: www.biu.ac.il
    Output: non-existent domain

    Input: mail.google.co.il
    Output: 1.2.3.9

Notes

Protocol: Communication between all components occurs using UDP.
Caching: The resolver caches both A and NS records. Expired entries are removed after x seconds.
Error Handling: If a domain cannot be resolved, the server returns non-existent domain.

Implementation Details

All components are implemented in Python.
Arguments to main must be passed via the command line.
Ensure strict adherence to input/output formats.
