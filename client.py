import socket
import dns.resolver
import pickle


server_ip = '67.184.42.68'
port = 19132

def main():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((server_ip, port))
    query_name = client_sock.recv(1024)
    print(f'We need to query {query_name.decode()}')
    resolver = dns.resolver.Resolver()
    resolver.timeout = 1
    resolver.lifetime = 1
    try:
        answers = resolver.resolve(query_name.decode(), 'A')
    except Exception as e:
        pass

    #doesn't matter if failure (failure is expected)
    serial_data = client_sock.recv(1024)
    org_name, my_ip = pickle.loads(serial_data)
    print(f"Your IP is: {my_ip}\nDNS Organization: {org_name}")

    


if __name__ == "__main__":
    main()