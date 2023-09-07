import socket
from umodbus import conf
from umodbus.client import tcp as modbus_tcp

# Enable values to be signed (default is False).
conf.SIGNED_VALUES = True

### Creating connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.100.103', 502))

# Create a message to write multiple coils
message = modbus_tcp.write_multiple_coils(slave_id=1, starting_address=1, values=[1])

# Send the message and get the response
response = modbus_tcp.send_message(message, sock)
print(response)

# Close the socket connection
sock.close()
print("Transfer finished")