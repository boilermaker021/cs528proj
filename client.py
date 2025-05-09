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
http_port = 19134

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
    
    webbrowser.open('http://' + str(query_name.decode()) + f':{http_port}') #this ensures DNS query behavior consistent with web broswing

    #doesn't matter if failure (failure is expected)
    serial_data = client_sock.recv(1024)
    org_name, dns_ip, my_ip = pickle.loads(serial_data)
    client_sock.close()
    return org_name, dns_ip, my_ip
    

def do_ipv6_check():
    client_sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    client_sock.settimeout(5)
    try:
        client_sock.connect((server_ip6, ipv6_port, 0, 0))
    except socket.timeout:
        return None
    ipv6 = client_sock.recv(1024)
    client_sock.close()
    return ipv6


def main():
    arg_len = len(sys.argv) - 1
    if arg_len == 0:
        print("Invalid usage! check readme")
        return
    default_if = sys.argv[1]
    #reuse http port for out-of-VPN traffic checking
    out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, default_if.encode())

    
    if (arg_len == 1):
        try:
            out.connect((server_ip, http_port))
            out.close()
            print('Out-of-VPN connetion established! Consider using a VPN that blocks traffic on other interfaces, or configure iptables rules to do this.')
        except Exception as e:
            print('Could not establish out-of-VPN connection! Your VPN setup blocks non-VPN traffic, preserving privacy!')
        #do one check without VPN activation
        dns_server_set = set()
        print("Testing with current system configuration...")
        for i in range(0,10):
            print(f"Test #{i}")
            org_name1, dns_ip1, my_ip1 = do_dns_check()
            print(f"Your IP is: {my_ip1}\nDNS IP: {dns_ip1}\nDNS Organization: {org_name1}")
            dns_server_set.add((org_name1, dns_ip1))
        try:
            ipv6_1 = do_ipv6_check()
            if ipv6_1 == None:
                print("Unable to establish ipv6 connection")
            else:
                print(f"Your IPv6 is: {ipv6_1}")
        except Exception as e:
            print("Could not route to ipv6")
        
    elif arg_len >= 2:
        #do 2 checks with VPN activation
        ipv6_1 = None
        ipv6_2 = None
        config_path = sys.argv[2]
        vpn_command = ['sudo', 'openvpn', config_path]
        print("Testing without VPN...")
        dns_server_set1 = set()
        for i in range(0,10):
            org_name1, dns_ip1, my_ip1 = do_dns_check()
            dns_server_set1.add((org_name1, dns_ip1))
            print(f"Your IP is: {my_ip1}\nDNS IP: {dns_ip1}\nDNS Organization: {org_name1}")
        try:
            ipv6_1 = do_ipv6_check()
            if ipv6_1 == None:
                print("Unable to establish ipv6 connection")
            else:
                print(f"Your IPv6 is: {ipv6_1}")
        except Exception as e:
            print("Could not route to ipv6")
        
        print("Activating VPN...\n")

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)


        process = subprocess.Popen(vpn_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(10)
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) #this resets terminal graphical settings so the openVPN output doesn't ruin further output

        print("Testing with VPN...")

        try:
            out.connect((server_ip, http_port))
            out.close()
            print('Out-of-VPN connetion established! Consider using a VPN that blocks traffic on other interfaces, or configure iptables rules to do this.')
        except Exception as e:
            print('Could not establish out-of-VPN connection! Your VPN setup blocks non-VPN traffic, preserving privacy!')
        dns_server_set2 = set()
        for i in range(0,10):
            org_name2, dns_ip2, my_ip2 = do_dns_check()
            dns_server_set2.add((org_name2, dns_ip2))
            print(f"Your IP is: {my_ip2}\nDNS IP: {dns_ip2}\nDNS Organization: {org_name2}")
        try:
            ipv6_2 = do_ipv6_check()
            if ipv6_2 == None:
                print("Unable to establish ipv6 connection")
            else:
                print(f"Your IPv6 is: {ipv6_2}")
        except Exception as e:
            print("Could not route to ipv6")

        process.terminate()
        process.wait()

        if (org_name1 == org_name2):
            print("The same organization handles your DNS requests with and without the VPN\nYou may be vulnerable to de-anonymization, especially if your DNS provider is your ISP!")
        else:
            print("Different organizations handle your DNS requests with and without the VPN\nYou are likely safe from de-anonymizing behavior")

        intersect = dns_server_set1 & dns_server_set2
        if (len(intersect) != 0):
            print("Some DNS servers are present both before and after VPN Activation! You likely have a DNS leak!\n")

        if (ipv6_1 == ipv6_2 and ipv6_1 != None):
            print("Your ipv6 remains the same with and without the VPN\nYou have an ipv6 leak. All ipv6 traffic will be routed through your ISP as if the VPN was absent.")

    


if __name__ == "__main__":
    main()