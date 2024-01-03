from rtspscanner import RTSPScanner
scanner = RTSPScanner()

# Set address to net wth CIDR notation or single host
scanner.address = '192.168.2.0/24'

# Set to scan mode (add/rem to/from rtsp-simple-server still under development and considered alpha)
scanner.mode = "scan"

# override default paths in csv (default shown)
# scanner.paths = "live,Streaming/Channels/101"

# override default credentials in csv (default is of type None)
# scanner.creds = "admin:admin,"user:pass"

# override default ports in csv (default shown)
# scanner.ports = "554,8554"

#run the scan
scanner.scanner()

# Print the list of cameras found as a dict
print(scanner.scanResults)