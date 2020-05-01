import socket
import io


server_address = ('127.0.0.1', 8080)

# create the socket with IPv4 and Stream type (TCP/ip4)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind socket to localhost:8080
server_socket.bind(server_address)
print('started:', server_socket)

# initializing InputStream of serversocket with 1 connection queue
server_socket.listen(1)

while True:
    print('\nwaiting for request ...')
    # Wait for an incomming connection and accept
    client_socket, client_address = server_socket.accept()
    print('connection accepted from:', client_address)

    try:
        # Read data
        while True:
            in_data = client_socket.recv(150)  # with 150 bytes of buffer
            in_data = in_data.decode('utf-8')
            print('\ninput data:', in_data)
            if in_data:
                try:
                    # eval function evaluates statement
                    answer = str(eval(in_data))
                except:
                    answer = 'error!'

                client_socket.sendall(answer.encode('utf-8'))
                print(f'Answered {in_data}')
            else:
                print('No data recived from', client_address)
                break
    finally:
        client_socket.close()
        print('connection closed')
