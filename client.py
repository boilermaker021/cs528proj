import socket
import dns.resolver
import pickle
import time
import subprocess
import os
import sys
import termios
import webbrowser

#Ips of my home network (where the server is running)
server_ip = '67.184.42.68'
server_ip6 = '2601:249:100:95c0::2177'


config_path = 'good.ovpn'
vpn_command = ['sudo', 'openvpn', config_path]
port = 19132
ipv6_port = 19133

def do_dns_check():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((server_ip, port))
    query_name = client_sock.recv(1024)
    #print(f'We need to query {query_name.decode()}')
    #resolver = dns.resolver.Resolver()
    #resolver.timeout = 1
    #resolver.lifetime = 1
    #try:
        #answers = resolver.resolve(query_name.decode(), 'A')
    #except Exception as e:
        #pass
    
    webbrowser.open(str(query_name.decode())) #this ensures DNS query behavior consistent with web broswing

    #doesn't matter if failure (failure is expected)
    serial_data = client_sock.recv(1024)
    org_name, dns_ip, my_ip = pickle.loads(serial_data)
    client_sock.close()
    return org_name, dns_ip, my_ip
    

def do_ipv6_check():
    client_sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    client_sock.connect((server_ip6, ipv6_port))
    ipv6 = client_sock.recv(1024)
    client_sock.close()
    return ipv6


def main():
    arg_len = len(sys.argv) - 1
    if (arg_len == 0):
        #do one check without VPN activation
        print("Testing with current system configuration...")
        org_name1, dns_ip1, my_ip1 = do_dns_check()
        print(f"Your IP is: {my_ip1}\nDNS IP: {dns_ip1}\nDNS Organization: {org_name1}")
        try:
            ipv6_1 = do_ipv6_check()
            print(f"Your IPv6 is: {ipv6_1}")
        except Exception as e:
            print("Could not route to ipv6")
        
    else:
        #do 2 checks with VPN activation
        ipv6_1 = None
        ipv6_2 = None
        config_path = sys.argv[1]
        vpn_command = ['sudo', 'openvpn', config_path]
        print("Testing without VPN...")
        org_name1, dns_ip1, my_ip1 = do_dns_check()
        print(f"Your IP is: {my_ip1}\nDNS IP: {dns_ip1}\nDNS Organization: {org_name1}")
        try:
            ipv6_1 = do_ipv6_check()
            print(f"Your IPv6 is: {ipv6_1}")
        except Exception as e:
            print("Could not route to ipv6")
        
        print("Activating VPN...\n")

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)


        process = subprocess.Popen(vpn_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(10)
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        print("Testing with VPN...")
        org_name2, dns_ip2, my_ip2 = do_dns_check()
        #ipv6_2 = do_ipv6_check()
        print(f"Your IP is: {my_ip2}\nDNS IP: {dns_ip2}\nDNS Organization: {org_name2}")
        try:
            ipv6_2 = do_ipv6_check()
            print(f"Your IPv6 is: {ipv6_2}")
        except Exception as e:
            print("Could not route to ipv6")

        process.terminate()
        process.wait()

        if (org_name1 == org_name2):
            print("The same organization handles your DNS requests with and without the VPN\nYou likely have a DNS leak!")
        else:
            print("Different organizations handle your DNS requests with and without the VPN\nYou are likely safe from DNS leak!")

        if (ipv6_1 == ipv6_2 and ipv6_1 != None):
            print("Your ipv6 remains the same with and without the VPN\nYou have an ipv6 leak. All ipv6 traffic will be routed through your ISP as if the VPN was absent.")

    


if __name__ == "__main__":
    main()