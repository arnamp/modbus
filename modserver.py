from pymodbus.server.sync import ModbusTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

# Define the data store (Holding Registers)
data = [0] * 100  # Initialize with zeros
store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, data))

context = ModbusServerContext(slaves=store, single=True)

# Create a Modbus TCP server
server = ModbusTcpServer(context, address=('169.254.96.214', 502))  # Use appropriate IP and port

# Start the server
print("Modbus TCP Server listening on {}:{}".format(server.address[0], server.address[1]))
server.serve_forever()