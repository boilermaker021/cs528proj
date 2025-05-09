# Report Details

The report is included in the zip file submission, as well as our powerpoint. The powerpoint is called "CS528 Final Presentation.pdf". The report is called "cs528_report.pdf".

# How to use
Ensure python3 and the required dependencies are installed. If you have openVPN and want to use one of the provided .ovpn files (or your own .ovpn files), provide the file name as the only parameter to `client.py`. If you want to use your own VPN or don't want the client to launch the VPN, don't provide any parameters to `client.py`.


# Required Packages
`dnspython dnslib ipwhois`


# Usage With Own Server
To use the tool, ensure that you have a server running, with ports 19132-19134 forwarded. In addition, replace the IPs and domain names in the server and client.py as necessary, then run the server with `sudo python server.py`. Then, execute the client as described in the steps below.

# Usage With Our Server
To use the tool with our server, simply excecute the client as described in the steps below.

# Client Execution
To simply gather information about your current connection (DNS servers, ipv6 status, etc) simply excecute `python client.py <default interface name>`, where default interface name is the name of the network interface you use for normal internet use. To include VPN Activation for automatic before/after comparison with the tool., run `python client.py <default interface name> <openvpn config file path>`, where openvpn config file path is the path to the openvpn configuration that you want to test.