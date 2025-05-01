import socket
import dns.resolver
import pickle
import time
import subprocess
import os
import sys
import termios


server_ip = '67.184.42.68'
config_path = 'good.ovpn'
vpn_command = ['sudo', 'openvpn', config_path]
port = 19132

def do_check():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((server_ip, port))
    query_name = client_sock.recv(1024)
    #print(f'We need to query {query_name.decode()}')
    resolver = dns.resolver.Resolver()
    resolver.timeout = 1
    resolver.lifetime = 1
    try:
        answers = resolver.resolve(query_name.decode(), 'A')
    except Exception as e:
        pass

    #doesn't matter if failure (failure is expected)
    serial_data = client_sock.recv(1024)
    org_name, dns_ip, my_ip = pickle.loads(serial_data)
    return org_name, dns_ip, my_ip
    

def main():
    print("Testing without VPN...")
    org_name1, dns_ip1, my_ip1 = do_check()
    print(f"Your IP is: {my_ip1}\nDNS IP: {dns_ip1}\nDNS Organization: {org_name1}")
    print("Activating VPN...\n")

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)


    process = subprocess.Popen(vpn_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10)
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    print("Testing with VPN...")
    org_name2, dns_ip2, my_ip2 = do_check()
    print(f"Your IP is: {my_ip2}\nDNS IP: {dns_ip2}\nDNS Organization: {org_name2}")

    process.terminate()
    process.wait()

    if (org_name1 == org_name2):
        print("The same organization handles your DNS requests with and without the VPN\nYou likely have a DNS leak!")
    else:
        print("Different organizations handle your DNS requests with and without the VPN\nYou are likely safe from DNS leak!")

    


if __name__ == "__main__":
    main()