
import socket  # 导入 socket 模块
import threading
import time

import utils

ADDRESS = ('127.0.0.1', 6666)  # 绑定地址
g_socket_server = None  # 负责监听的socket
g_conn_pool = []  # 连接池
#g_data_msg = []
g_data_msg = {'p1': 0, 'p2': 0}


def init():
    """
    初始化服务端
    """
    global g_socket_server
    g_socket_server = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)  # 创建 socket 对象
    g_socket_server.bind(ADDRESS)
    g_socket_server.listen(5)  # 最大等待数（有很多人理解为最大连接数，其实是错误的）
    print("服务端已启动，等待客户端连接...")


def accept_client():
    """
    接收新连接
    """
    while True:
        client, _ = g_socket_server.accept()  # 阻塞，等待客户端连接
        # 加入连接池
        g_conn_pool.append(client)
        # 给每个客户端创建一个独立的线程进行管理
        thread = threading.Thread(target=message_handle, args=(client,))
        # 设置成守护线程
        thread.setDaemon(True)
        thread.start()


def message_handle(client):
    """
    消息处理
    """
    client.sendall("连接服务器成功!".encode(encoding='utf8'))
    while True:
        data_recv = utils.receiveAndReadSocketData(client)
        #print("客户端消息:", data_recv)
        id = data_recv['id']
        g_data_msg[id] = data_recv['key']


if __name__ == '__main__':
    init()
    # 新开一个线程，用于接收新连接
    thread = threading.Thread(target=accept_client)
    thread.setDaemon(True)
    thread.start()
    # input()
    while True:
        client_numb = len(g_conn_pool)
        msg_recv_numb = len(g_data_msg)

        if g_data_msg['p2'] != 0 and g_data_msg['p1'] != 0:
            data_send = utils.packSocketData(
                {'p1_key': g_data_msg['p1'], 'p2_key': g_data_msg['p2']})
            g_conn_pool[0].sendall(data_send)
            g_conn_pool[1].sendall(data_send)
            g_data_msg['p1'] = 0
            g_data_msg['p2'] = 0

