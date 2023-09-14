import paho.mqtt.client as mqtt
import mysql.connector
import random
import json
import queue
import time
import threading
from pymodbus.client.sync import ModbusTcpClient
import socket
from umodbus import conf
from umodbus.client import tcp as modbus_tcp

# Create Queue Handle
q = queue.Queue()

word_485 = "485 Transceiver(D485ZT)"

broker = 'en-apis.zifisense.com'
port = 1883
topic =  "980f70347bc145c8a0adb4a34a76b264/jll/property/ms/+/updata"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = '980f70347bc145c8a0adb4a34a76b264'
password = 'a7ae992006b5486bbda172e1752303aa'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Connected")
        else:
            print("MQTT Not Connect")
    # Set Connecting Client ID
    client = mqtt.Client(client_id,protocol=mqtt.MQTTv31)
    print("Client ID: ",client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt):
    def on_message(client, userdata, msg):
        global q
        decoded_text = msg.payload.decode("utf-8")
        #print("decoded_text is ",decoded_text)
        try:
            json_res = json.loads(decoded_text)
         #   print("json is ",json_res)
            q.put(json_res)
        except:
            print("The incoming data is not json!!")
        print(" ------------------------------ ")
        return

    client.subscribe(topic)
    client.on_message = on_message

def insert_data(CompanyCode,DeviceType,Data,Temp,Humid,Info,Datetime):
   #ทำการเชื่อมต่อกับฐานข้อมูลง่าย ๆ แค่ใส่ Host / User / Password ให้ถูกต้อง
    vibra_db = mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        port=3306,
        user="sql12646206",
        password="7T2ruFRBUV",
        database = "sql12646206"
    )

    db_cursor = vibra_db.cursor()

    sql = "insert into project(CompanyCode,DeviceType,Data,Temp,Humid,Info,datetime) values(%s,%s,%s,%s,%s,%s,%s)"
    val=(str(CompanyCode),str(DeviceType),str(Data),str(Temp),str(Humid),str(Info),str(Datetime))
    db_cursor.execute(sql,val)

    vibra_db.commit()
    vibra_db.close()

def processQueueTask(q):
    start = {}
    end = {}
    json_get = ""
    while(1):
        print("-------- processTask ---------")
        try:
            if (q.empty() == True):
                print("No any data is Queue!!")
            else:
                json_get = q.get()
                print("json_get = ",json_get)
                with open('data.text', 'w') as json_file:
                    json.dump(json_get, json_file, indent=4) 
                with open("data.text", "r") as file:
                    for line_number, line in enumerate(file, start=1):  
                        if word_485 in line:
                            with open('data.text') as fs:
                                data_filter = fs.read()
                                data = json.loads(data_filter)
                                company_data = data['companyCode']
                                print("CompanyCode : ",company_data)
                                device = data['deviceAlias']
                                print("DeviceType : ",device)
                                bit_data_Temphumid485 = data['data']
                                print('Data_Temp485 :',bit_data_Temphumid485)
                                # Decode Bit Temp
                                bit_Temp485 = (bit_data_Temphumid485[8:12])
                                print('Bit_Temp485 :', bit_Temp485)
                                decode_bit_temp485 = int(bit_Temp485,16)*0.1
                                print('Temp485 : %.2f Celsius' %decode_bit_temp485)
                                # Decode Bit Humid
                                bit_humid485 = (bit_data_Temphumid485[4:8])
                                print('Bit Humid485 : ',bit_humid485)
                                decode_bit_humid485 = int(bit_humid485,16)
                                print('Humid485 : {} RH%'.format(decode_bit_humid485))
                                Temp485 = "{:.2f}".format(decode_bit_temp485)
                                Humid485 = decode_bit_humid485
                                Info_rs485 = 'Temp : {} Celcius , Humid : {} RH%'.format(Temp485,Humid485)
                                unixtime = data['upTime']
                                print("unix time : ",unixtime)
                                datetime = time.localtime(unixtime)
                                strdatetime = (time.strftime("%Y-%m-%d %H:%M:%S", datetime))
                                print(strdatetime)
                                insert_data(company_data,device,bit_data_Temphumid485,Temp485,Humid485,Info_rs485,strdatetime)
                                # PLC's IP address and Modbus TCP port
                                PLC_IP = '192.168.100.103'
                                PLC_PORT = 502

                                # Modbus address (register number) to write data to
                                REGISTER_ADDRESS1 = 1 # Replace with the actual register address
                                REGISTER_ADDRESS2 = 2

                                # Data to send to the PLC
                                data_to_send1 = [round(Temp485)]  # Replace with your data
                                data_to_send2 = [Humid485]

                                # Connect to the PLC
                                client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
                                if client.connect():
                                    print("Connected to PLC")

                                    # Write data to the Modbus register
                                    try:
                                        client.write_registers(REGISTER_ADDRESS1, data_to_send1)
                                        print("Data sent successfully to address 1 : ", data_to_send1)
                                        client.write_registers(REGISTER_ADDRESS2, data_to_send2)
                                        print("Data sent successfully to address 2 : ", data_to_send2)
                                    except Exception as e:
                                        print("Error writing data:", e)
                                    finally:
                                        # Close the Modbus connection
                                        client.close()

                                # Enable values to be signed (default is False).
                                conf.SIGNED_VALUES = True
                                ### Creating connection
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.connect(('192.168.100.103', 502))

                                data_control = round(Temp485)

                                # Create a message to write multiple coils
                                message = modbus_tcp.write_multiple_coils(slave_id=1, starting_address=0, values=[1])
                                message2 = modbus_tcp.write_multiple_coils(slave_id=1, starting_address=0, values=[0])
                                # Send the message and get the response
                                if data_control>25:
                                    response = modbus_tcp.send_message(message, sock)
                                    print("send {} to address 0 ".format(response))
                                else:
                                    response2 = modbus_tcp.send_message(message2,sock)
                                    print("send {} to address 0 ".format(response2))

                                # Close the socket connection
                                sock.close()
                                print("Transfer finished")

        except:
            print("Error")
        time.sleep(5) # delay for 5 sec.
    return

worker = threading.Thread(target=processQueueTask, args=(q,), daemon=True) # create python thread (like xTaskCreate in platform IO)
worker.start()

client = connect_mqtt()
subscribe(client)
client.loop_forever()
