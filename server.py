import socket
import threading
import utils

ADDRESS = ('127.0.0.1', 6666)
g_socket_server = None
g_conn_pool = []
#g_data_msg = []
g_data_msg = {'p1': 0, 'p2': 0}


def init(addr):
    """
    初始化服务端
    """
    global g_socket_server
    g_socket_server = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    g_socket_server.bind(addr)
    g_socket_server.listen(5)
    print("服务端已启动，等待客户端连接...")


def accept_client():
    """
    接收新连接
    """
    while True:
        client, _ = g_socket_server.accept()

        g_conn_pool.append(client)

        thread = threading.Thread(target=message_handle, args=(client,))

        thread.setDaemon(True)
        thread.start()


def message_handle(client):
    """
    消息处理
    """
    client.sendall("连接服务器成功!".encode(encoding='utf8'))
    while True:
        data_recv = utils.receiveAndReadSocketData(client)
        #print(client, "客户端消息:", data_recv)
        id = data_recv['id']
        msg = []
        msg.append(data_recv['key'])
        msg.append(data_recv['mouse_move_pos'])
        msg.append(data_recv['mouse_down_pos'])
        msg.append(data_recv['player_health'])

        g_data_msg[id] = msg
       #g_data_msg[id] = data_recv['key']

def start_server(addr = ADDRESS):
    init(addr)
    # pygame.init()

    thread = threading.Thread(target=accept_client)
    thread.setDaemon(True)
    thread.start()

    while True:

        # passtime=clock.tick(20)
        if g_data_msg['p2'] != 0 and g_data_msg['p1'] != 0:

            data_send = utils.packSocketData(
                {'p1_key': g_data_msg['p1'][0], 'p2_key': g_data_msg['p2'][0], 'p1_mouse_move_pos': g_data_msg['p1'][1], 'p2_mouse_move_pos': g_data_msg['p2'][1], 'p1_mouse_down_pos': g_data_msg['p1'][2], 'p2_mouse_down_pos': g_data_msg['p2'][2], 'p1_player_health': g_data_msg['p1'][3], 'p2_player_health': g_data_msg['p2'][3]})

            g_conn_pool[0].sendall(data_send)
            g_conn_pool[1].sendall(data_send)
            #print(data_send)
            g_data_msg['p1'] = 0
            g_data_msg['p2'] = 0

if __name__ == '__main__':
    start_server()
