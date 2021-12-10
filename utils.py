import os
import json

'''接收并读取网络数据'''
def receiveAndReadSocketData(socket):
    data = ''
    while True:
        data_part = socket.recv(1024).decode()
        if 'END' in data_part:
            data += data_part[:data_part.index('END')]
            break
        data += data_part
    return json.loads(data, encoding='utf-8')


'''包装待发送数据'''
def packSocketData(data):
    return (json.dumps(data)+' END').encode()