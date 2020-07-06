import socket
import os
import base64
import magic


class Client:
    address = None
    buffer_size = None
    client_socket = None
    request = None
    response = None
    connection_life = "Keep-Alive"

    def __init__(self, buff_size=4096000):
        self.buffer_size = int(buff_size)

    def send_request(self, address):
        # initiating a socket for client in TCP/IPv4 and given port and making the port reuseable
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.address = self.tokenize_address(address)

        try:
            self.client_socket.connect(
                (self.address['host'], int(self.address['port'])))
            print(
                f"\nConnection created with: {self.address['host']}:{self.address['port']}")
            print()
            # send the query
            print(
                f'Sending GET request to {self.address["host"]}:{self.address["port"]} ...'
            )

            self.request = self.create_get_request()
            self.client_socket.sendall(self.request)

            # read the response
            # getting full response from buffer then tokenizing it
            # response is a dictionary with all headers and content
            response_raw = self.client_socket.recv(
                self.buffer_size)

            self.response = self.tokenize_response(response_raw)
            print(
                f'Response : {self.response["status"]} {self.response["status_code"]}\n'
            )

            self.response_decode()

        finally:
            self.client_socket.close()
            print('\nClient socket closed')

        return self.response

    def response_decode(self):
        content = self.response['content']
        mime = magic.from_buffer(content, mime=True)

        if mime == 'image/jpeg':
            pass
        else:
            self.response['content'] = self.response['content'].decode('utf-8')

    def tokenize_address(self, address):
        address_dict = {}
        address = address.split(':')

        if "http" in address[0] or "https" in address[0]:
            address_dict['protocol'] = address.pop(0)
            address_dict['host'] = address.pop(0)[2:].split('/')[0]
        else:
            address_dict['protocol'] = "http"
            address_dict['host'] = address.pop(0).split('/')[0]

        address = ''.join(address).split('/')

        address_dict['port'] = address.pop(0)
        if address_dict['port'] == "":
            address_dict['port'] = 80

        if len(address) == 1 or len(address) == 0:
            address_dict['path'] = '/'
        else:
            address_dict['path'] = '/' + '/'.join(address)

        return address_dict

    def tokenize_response(self, response):
        response_dict = {}
        # spliting response data to lines
        tmp = b''
        header = b''
        pattern = b''
        for i in range(len(response)):
            pattern += response[i:i+1]
            if pattern.decode().find("\r\n\r\n") != -1:
                break
            else:
                header += response[i:i+1]
                tmp = response[i:i+1]
        header = header[:i-3].decode('utf-8').split('\n')
        response_dict['content'] = response[i+1:]

        first_tag, tags = header[0], header[1:]
        # spliting first line=> status, status code, protocol & version
        tmp = first_tag.split(' ')
        response_dict['protocol'], response_dict['version'] = tmp[0].split('/')
        response_dict['status'] = tmp[1]
        response_dict['status_code'] = tmp[2]

        # data after the first line :
        for i, tag in enumerate(tags):
            if tag != '':
                # getting rid of \n in the left side of lines and splitting them to tag : value
                tmp = tag.lstrip().rstrip().split(': ')
                response_dict[tmp[0]] = tmp[1]

        return response_dict

    def create_get_request(self):
        request = '\r\n'.join((
            f"GET {self.address['path']} HTTP/1.1",
            f"Host: {self.address['host']}",
            f"Connection: {self.connection_life}" + "\r\n\r\n",
        )).encode('utf-8')
        return request


if __name__ == '__main__':
    client = Client()  # create the client instans
    # request to host:port
    # client.send_request('127.0.0.1:1234/')
    # client.send_request('127.0.0.1:1234/docs/test.jpg')
    client.send_request('google.com')
