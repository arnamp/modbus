from pymodbus.client.sync import ModbusTcpClient

# PLC's IP address and Modbus TCP port
PLC_IP = '127.0.0.1'
PLC_PORT = 502

# Modbus address (register number) to write data to
REGISTER_ADDRESS = 0 # Replace with the actual register address

# Data to send to the PLC
data_to_send = [65]  # Replace with your data

# Connect to the PLC
client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
if client.connect():
    print("Connected to PLC")

    # Write data to the Modbus register
    try:
        client.write_registers(REGISTER_ADDRESS, data_to_send)
        print("Data sent successfully:", data_to_send)
    except Exception as e:
        print("Error writing data:", e)
    finally:
        # Close the Modbus connection
        client.close()
else:
    print("kuy")
