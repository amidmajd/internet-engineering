import socket
import io
import threading


def run_server(server_address):
    # create the socket with IPv4 and Stream type (TCP/ip4)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind socket to address
    if int(server_address[0].split(".")[-1]) % 2 == 0:
        server_socket.bind(server_address)
    else:
        server_address = (server_address[0], server_address[1]+1000)
        server_socket.bind(server_address)
    print(f'started server {server_address}')

    # initializing InputStream of serversocket with 1 connection queue
    server_socket.listen(1)

    while True:
        # Wait for an incoming connection and accept
        client_socket, client_address = server_socket.accept()

        try:
            # Read data
            while True:
                in_data = client_socket.recv(150)  # with 150 bytes of buffer

                if in_data.decode('utf-8'):
                    client_socket.sendall('YES'.encode('utf-8'))
                    break
                else:
                    break
        finally:
            client_socket.close()
            print(f'connection with {server_address} closed')


threads = []
for modem_num in range(500):
    server_address = (f'127.0.0.{modem_num+2}', 917)

    t = threading.Thread(target=run_server, args=(server_address,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
