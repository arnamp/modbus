from pymodbus.client.sync import ModbusTcpClient

# Modbus TCP server IP address and port
SERVER_IP = '192.168.100.103'
SERVER_PORT = 502

# Create a Modbus TCP client
client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)

# Connect to the Modbus TCP server
client.connect()

# Modbus address to read from
MODBUS_ADDRESS = 0x01

# Number of registers to read
NUM_REGISTERS = 5

try:
    # Read multiple registers from the server
    response = client.read_holding_registers(MODBUS_ADDRESS, NUM_REGISTERS, unit=1)

    if response.isError():
        print("Modbus error:", response)
    else:
        # Print the values of the registers
        register_values = response.registers
        for i, value in enumerate(register_values):
            print(f"Register {MODBUS_ADDRESS + i}: {value}")

finally:
    # Close the Modbus TCP client connection
    client.close()