import socket
import threading
import time
import random
import string
from dnslib import DNSRecord

waiting_for_query = []
domain = "cs528proj.com"

#def handle_dns_query():
#    while True:


def main():
    #dns_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #dns_listener.bind(('localhost', 53))
    control_sock.bind(('localhost', 55555))
    control_sock.listen(5)
    print("Bound sockets")
    while True:
        client_sock, client_addr = control_sock.accept()
        rand_prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        query_name = f'{rand_prefix}.{domain}'
        while (query_name in waiting_for_query):
            query_name = f'{rand_prefix}.{domain}' #ensure unique query ID
        waiting_for_query.append(query_name)
        client_sock.sendall(query_name.encode())
        

if __name__ == "__main__":
    main()
