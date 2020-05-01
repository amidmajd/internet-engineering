import socket


server_address = ('127.0.0.1', 8080)

# create the socket with IPv4 and Stream type (TCP/ip4)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f'connecting to {server_address}')
client_socket.connect(server_address)

request = ''

try:
    while True:
        # read the request
        request = input('\nWhat is your math question? [sample: 5*8+4] ')
        if request == 'done':
            break
        # send the query
        client_socket.sendall(request.encode('utf-8'))

        # read the answer from the server
        in_data = client_socket.recv(100)  # receving input data with 100bytes of buffer size
        in_data = in_data.decode('utf-8')
        print(f'The answer of {request} is {in_data}.')

finally:
    client_socket.close()
    print('connection closed')
