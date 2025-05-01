import socket
import threading
import time
import random
import string
from dnslib import DNSRecord

waiting_for_query = {}
domain = "cs528proj.com"

def handle_dns_query(dns_listener: socket.socket):
    while True:
        data, src = dns_listener.recvfrom(1024)
        dns_req = DNSRecord.parse(data)
        qname = dns_req.q.qname
        if (qname in waiting_for_query):
            dest_sock = waiting_for_query[qname]
            del waiting_for_query[qname]
            ip_addr, port = src
            hostname, _, _ = socket.gethostbyaddr(ip_addr)
            print(f'hostname: {hostname}')


def main():
    dns_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    dns_listener.bind(('localhost', 53))
    control_sock.bind(('localhost', 55555))
    control_sock.listen(5)
    print("Bound sockets")
    dns_thread = threading.Thread(target=handle_dns_query, args=(dns_listener))
    dns_thread.start()
    while True:
        client_sock, client_addr = control_sock.accept()
        rand_prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        query_name = f'{rand_prefix}.{domain}'
        while (query_name in waiting_for_query):
            query_name = f'{rand_prefix}.{domain}' #ensure unique query ID
        waiting_for_query[query_name] = client_sock
        client_sock.sendall(query_name.encode())
        

if __name__ == "__main__":
    main()
