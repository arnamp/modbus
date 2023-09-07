import socket
from pyModbusTCP.server import ModbusServer

# Get the IP address of the Raspberry Pi
server_ip_address = "0.0.0.0"  # Listen on all network interfaces
server_port = 502

# Create an instance of ModbusServer
server = ModbusServer(server_ip_address, server_port, no_block=True)

server.start()