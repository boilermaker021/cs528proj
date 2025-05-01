import socket
import threading
import time
import random
import string
import dns.reversename
from dnslib import DNSRecord
import dns.resolver
from ipwhois import IPWhois

waiting_for_query = {}
domain = "cs528proj.com"

port = 19132

def handle_dns_query(dns_listener: socket.socket):
    while True:
        data, src = dns_listener.recvfrom(1024)
        #print("incoming DNS request!")
        dns_req = DNSRecord.parse(data)
        qname = str(dns_req.q.qname).lower()[:-1]
        #print(f"name: {qname}")
        if ((qname) in waiting_for_query):
            dest_sock = waiting_for_query[qname]
            del waiting_for_query[qname]
            ip_addr, port = src
            lookup = IPWhois(str(ip_addr))
            res = lookup.lookup_rdap()
            print(f"ipwhois: {res}")
            


def main():
    dns_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    dns_listener.bind(('0.0.0.0', 53))
    control_sock.bind(('0.0.0.0', port))
    
    control_sock.listen(5)
    print("Bound sockets")
    dns_thread = threading.Thread(target=handle_dns_query, args=(dns_listener,))
    dns_thread.start()
    while True:
        client_sock, client_addr = control_sock.accept()
        rand_prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        query_name = f'{rand_prefix}.{domain}'.lower()
        while (query_name in waiting_for_query):
            query_name = f'{rand_prefix}.{domain}'.lower() #ensure unique query ID
        waiting_for_query[query_name] = (client_sock, client_addr)
        client_sock.sendall(query_name.encode())
        

if __name__ == "__main__":
    main()
