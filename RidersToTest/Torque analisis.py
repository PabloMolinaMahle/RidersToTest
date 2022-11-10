# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 12:43:40 2022

@author: M0188337
"""

from textwrap import wrap
import tkinter as tk
from tkinter import filedialog
import csv

class RawDataMessage:
    time: float
    torque: float
            
class Main():
    def run(self):
        
        # Read data
        data = self.ReadData()
        
        # Debug
        # for item in data:
            # print("Time: " + str(item.time) + " Torque: " + str(item.torque))
        
        # Save data
        f = open('export.csv', 'w', newline='')
        writer = csv.writer(f, delimiter =';')
        
        prevTime = 0.0
        prevTorque = 0.0
        firstElement = True
        
        for item in data:
            tempDelta = 0
            if firstElement:
                tempDelta = 0.0
                firstElement = False
            else:
                tempDelta = (float(item.torque)-float(prevTorque))/(float(item.time)-float(prevTime))
                print("dT= " + str(float(item.torque)-float(prevTorque)) + " dt= " + str(float(item.time)-float(prevTime)) + " dT/dt= " + str(tempDelta))
            row = [str(item.time).replace(".", ","), str(item.torque).replace(".", ","), str(tempDelta).replace(".", ",")]
            writer.writerow(row)
            prevTime = item.time
            prevTorque = item.torque
            
        f.close()
    
    def ReadData(self):


        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename()
        # selectedFile = QFileDialog.getOpenFileName("Choose data file","C:\\Users\\M0188337\\Desktop\\M20 script test\\", "Data file (*.log *.trc *.txt) ")
        
        print("Read file data")
        
        
        
        print("File datalogger: " + file_path)
        
        # Open file
        data = open(file_path, "r", encoding="utf8")
        
        # Read file data
        datos = data.readlines()
        
        # List to store splited data
        splitedData = []
        
        # Start reading data and spliting
        for item in datos:
            # Check if is a line to process
            if item[0] != "#" and item[0] != "T" and item[0] != "" and item[0] != " " and item[0] != "\n":
                
                # First split
                # print("Line: " + item)
                time, messageType, can, trace = item.replace("\n", "").split(";")
                
                # Debug
                # print("Can: " + str(can) + " Trace: " + str(trace))
                
                # Filter Torque sensor 1 messages                
                if can == "100":
                    
                    # print("Can: " + str(can) + " Trace: " + str(trace))
                    
                    # initzialice new raw data variable
                    currRawDatamessage = RawDataMessage()
    
                    # process time
                    #self.currRawDatamessage.time = self.processTime(self.time)
                    currRawDatamessage.time = self.processTime(time)
                    
                    # process can message and extract torque info
                    currRawDatamessage.torque = self.GetTorqueValue(trace)
                    
                    # append data
                    splitedData.append(currRawDatamessage)
                    
                    # print("Torque: " + str(currRawDatamessage.torque))
        
        # Debug
        # for item in self.splitedData:
        #     print(item)
            
        return splitedData
    
    # Method to process time variable
    def processTime(self, timeToProcess):

        lenght = len(timeToProcess)
        
        # print("Time to process: " + timeToProcess)
        
        mili = timeToProcess[lenght - 3:lenght]
        
        # print("Mili: " + mili)
        
        second = timeToProcess[lenght - 5:lenght - 3]
        
        # print("second: " + second)
        
        minute = timeToProcess[lenght - 7:lenght - 5]
        
        # print("minute: " + minute)
        
        hour = timeToProcess[lenght - 9:lenght - 7]
        
        # prisnt("hour: " + hour)
        
        # day = timeToProcess[lenght - 11:lenght - 9]
        
        # print("day: " + day)
        
        # year = timeToProcess[:4]
        
        # month = timeToProcess[4:6]
        
        # day = timeToProcess[6:8]
        
        # hour = timeToProcess[8:10]
        
        # minute = timeToProcess[10:12]
        
        # second = timeToProcess[12:14]
        
        # mili = timeToProcess[4:6]
        
        dateAndTime = str(int(second) + int(minute)*60 + int(hour)*3600) + "." + str(mili)
        
        # Debug
        # print("Date and time: " + dateAndTime)
        
        return dateAndTime
    
    def GetTorqueValue(self, message):
        
        # print("Message: " + message)
        
        orderedMessage = self.PrepareMessage(message)
        
        # print("orderedMessage: " + orderedMessage)
        
        variableRawData = self.VariableDataFromMessage(orderedMessage, 20, 16)

        # print("Ordered message: " + orderedMessage + " Raw variable: " + variableRawData)

        # Convert to dec
        decResult = int(variableRawData, 2)
        # Debug
        # print("Extract Dec: " + str(decResult))
        
        # Apply gain
        decResult *= float(0.01)
        
        # Apply offset
        decResult += float(-327.67)
        
        # Debug
        # print ("Processed Dec: " + str(decResult))
        
        return decResult
    
    def PrepareMessage(self, message):
        # Get message lenght
        messageLength = 4*len(message)
        
        # print("Message lenght: " + str(messageLength) + " lenght: " + str(len(message)) + " Message: " + str(message))
        
        # print("Binary lenght: " + str(len(message)) + " str: " + str(message))
        
        # Convert HEX message to BIN and remove "0b" characters
        messageBinary = bin(int(message,16))[2:]
        
        # print("Bin message: " + str(messageBinary) + " lenght: " + str(len(messageBinary)))
        
        # Fill with 0 on the left to the message lenght
        messageBinaryString = messageBinary.zfill(messageLength)
        # print("zfill lenght: " + str(len(messageBinaryString)) + " str: " + str(messageBinaryString))
        
        # Fill with 0 on the right to 64 bit lenght
        
        # print("Message zero left: " + messageBinaryString + " Lenght: " + str(len(messageBinaryString)))
        messageBinaryString =  messageBinaryString.ljust(64, '0')
        # print("Message zero right: " + str(messageBinaryString) + " lenght: " + str(len(messageBinaryString)))
        
        # print("Message zero complete: " + messageBinaryString + " Force zeros: " + messageBinaryString.ljust(64, '0'))
        
        # Split number in groups of 8 (1 bytes) and return it
        byteList = wrap(messageBinaryString, 8)
        
        # Debug
        # for byte in byteList:
        #     print("Byte: " + str(byte))
        
        # Invert bytes and concatenate
        
        orderedMessage = ""
        
        for byte in byteList:
            orderedMessage += str(byte[::-1])
            
        # Debug
        # print("Ordered message: " + orderedMessage)
                
        # print("Message 1: " + DecodeAlgorithm.VariableDataFromMessage(orderedMessage, 0, 8))
        # print("Message 2: " + DecodeAlgorithm.VariableDataFromMessage(orderedMessage, 20, 16))
        # print("Message 3: " + DecodeAlgorithm.VariableDataFromMessage(orderedMessage, 36, 10))
        
        return orderedMessage
    
    def VariableDataFromMessage(self, orderedMessage, bitpos, lenght):
        
        # print("Message: " + orderedMessage + " Bitpos: " + str(bitpos) + " lenght: " + str(lenght))
        
        parcialMessage = orderedMessage[bitpos:(bitpos+lenght)]
        
        # print("Variable: " + parcialMessage[::-1])
                
        return parcialMessage[::-1]
    
    
    
if __name__ == '__main__':
    Main().run()
    