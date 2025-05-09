import socket
import threading
import time
import random
import string
import dns.reversename
from dnslib import DNSRecord, RR, QTYPE, A
import dns.resolver
from ipwhois import IPWhois
import pickle

waiting_for_query = {}
domain = "cs528proj.com"
own_ip = '67.184.42.68'

port = 19132
ipv6_port = 19133 #REMEMBER TO FORWARD THIS PORT LATER
http_port = 19134

def handle_dns_query(dns_listener: socket.socket):
    while True:
        data, src = dns_listener.recvfrom(1024)
        #print("incoming DNS request!")
        dns_req = DNSRecord.parse(data)
        qname = str(dns_req.q.qname).lower()[:-1]
        #print(f"name: {qname}")
        if ((qname) in waiting_for_query):
            client_sock, client_addr = waiting_for_query[qname]
            del waiting_for_query[qname]
            ip_addr, port = src
            lookup = IPWhois(str(ip_addr))
            res = lookup.lookup_rdap()
            #print(f"ipwhois: {res}")
            org_name = res.get("network", {}).get("name", None)
            #print(f"Organization: {org_name}")
            send_data = (org_name, str(ip_addr), str(client_addr))
            serial_data = pickle.dumps(send_data)
            client_sock.sendall(serial_data)
        #now send proper response
        reply = dns_req.reply()
        for q in dns_req.questions:
            qname = q.qname
            qtype = q.qtype
            if qtype == QTYPE.A:
                reply.add_answer(RR(qname, QTYPE.A, rdata=A(own_ip), ttl=60))
        #print(f'sending: {str(reply)} to {str(src)}')
        dns_listener.sendto(reply.pack(), src)



def handle_ipv6():
    ipv6_tester = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    ipv6_tester.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
    ipv6_tester.bind(('::', ipv6_port))
    ipv6_tester.listen(5)
    while True:
        client_sock, client_addr = ipv6_tester.accept()
        client_sock.send(client_addr) #just send own ipv6 back to client so they can know which one is being used (if same as original, then it means that there is a leak)
        client_sock.close()


def serve_http():
    http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    http_sock.bind(('0.0.0.0', http_port))
    http_sock.listen(5)
    file = open('close.html', 'r')
    content = file.read()

    http_response = (
        'HTTP/1.1 200 OK\r\n'
        'Content-Type: text/html; charset=utf-8\r\n'
        f'Content-Length: {len(content)}\r\n'
        'Connection: close\r\n'
        '\r\n' +
        content
    ).encode('utf-8')

    while True:
        client_sock, addr = http_sock.accept()
        client_sock.recv(1024)
        client_sock.sendall(http_response)
        client_sock.close()

            
            


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
    ipv6_thread = threading.Thread(target=handle_ipv6)
    ipv6_thread.start()

    http_thread = threading.Thread(target=serve_http)
    http_thread.start()
    while True:
        client_sock, client_addr = control_sock.accept()
        rand_prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        query_name = f'{rand_prefix}.{domain}'.lower()
        while (query_name in waiting_for_query):
            query_name = f'{rand_prefix}.{domain}'.lower() #ensure unique query ID (subdomain)
        waiting_for_query[query_name] = (client_sock, client_addr)
        client_sock.sendall(query_name.encode())
        

if __name__ == "__main__":
    main()
