import socket
import sys


def main():
    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = sys.argv[1]
    port = int(sys.argv[2])
    while True:
        # take input from the user and send it to the server
        to_send = input()
        s.sendto(to_send.encode(), (ip, port))
        data, addr = s.recvfrom(1024)
        data = data.decode()
        # if the data is non-existent domain, print it
        if data == "non-existent domain":
            print("non-existent domain")
        else:
            # print the ip
            print(data.split(",")[1])
    s.close()


if __name__ == "__main__":
    main()
