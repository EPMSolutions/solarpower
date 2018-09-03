#!/usr/bin/env python
 
# Modbus uitlezen
# Apparaat: EASTRON SDM120 (KWh meter)
#
# Script gemaakt door S. Ebeltjes (domoticx.nl)
 
from __future__ import division
import pymodbus
import serial
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient #initialize a serial RTU client instance
from pymodbus.transaction import ModbusRtuFramer
 
from pymodbus.constants import Endian              # Nodig voor 32-bit float getallen (2 registers / 4 bytes)
from pymodbus.payload import BinaryPayloadDecoder  # Nodig voor 32-bit float getallen (2 registers / 4 bytes)
from pymodbus.payload import BinaryPayloadBuilder  # Nodig om 32-bit floats te schrijven naar register
import paho.mqtt.client as mqtt
import json
 
method = "rtu"
port = "/dev/ttyUSB1"
baudrate = 2400
stopbits = 1
bytesize = 8
parity = "N"
timeout = 1
retries = 2
slaveId = 0x01
clientId = 'A00001'
deviceId = 'C00001'

broker="192.168.1.103"

registers = {0x0000:"V", 0x0006:"A", 0x000c:"W", 0x0012: "VA", 0x0156:"kWhA", 0x0158:"kWh", 0x0046: "Hz", 0x001e :"Pf"}
mqttServer= mqtt.Client("client-001") 


try:
	client = ModbusClient(method = method, port = port, stopbits = stopbits, bytesize = bytesize, parity = parity, baudrate = baudrate, timeout = timeout, retries = retries)
	connection = client.connect()
except:
	print "Modbus connectie error / EASTRON SDM120"
	client.close()

def read(register, slaveId):
	try:
		data =client.read_input_registers(register,2,unit=slaveId)
		decoder = BinaryPayloadDecoder.fromRegisters(data.registers, Endian.Big) # endian=Endian.Little / endian=Endian.Big
		val = round(decoder.decode_32bit_float(), 3)
	
		client.close()
		return val
	except  Exception as e:
		print "Modbus register "+str(register)+ " error"
		print e.message
		#client.close();
		return 0

data = {}
data["device"] = deviceId
for (address, unit) in registers.items():
	value = read(address,slaveId)
	data[str(unit)] = str(value);
	print (str(unit)+'#'+ ': ' + str(value))
	
#print str(read(0x0000,slaveId)) + ' V'
#print str(read(0x0006,slaveId)) + ' A'
#print str(read(0x000c,slaveId)) + ' W'
#print str(read(0x0012,slaveId)) + ' VA'
#print str(read(0x0156,slaveId)) + ' kWh'
#print str(read(0x0158,slaveId)) + ' kWh'
#print str(read(0x0046,slaveId)) + ' Hz'
#print str(read(0x001e,slaveId)) + ' Pf'
print("connecting to broker ",broker)
mqttServer.connect(broker)#connect
mqttServer.publish("client/"+clientId+'/device/'+deviceId,json.dumps(data,separators=(',',':')))#publish
mqttServer.disconnect() #disconnect

#client.close()