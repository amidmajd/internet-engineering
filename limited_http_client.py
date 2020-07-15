import socket
import ssl
import os
import base64
import magic
import pdb
from urllib.parse import urlsplit


class Client:
    address = None
    buffer_size = None
    client_socket = None
    request = None
    response = None
    connection_life = "Keep-Alive"

    def __init__(self, buff_size=3276800):
        self.buffer_size = int(buff_size)

    def send_request(self, address):
        # initiating a socket for client in TCP/IPv4 and given port and making the port reuseable
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.address = self.tokenize_address(address)

        if self.address['protocol'] == "https":
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            self.client_socket = ssl_context.wrap_socket(
                self.client_socket, server_hostname=self.address["host"]
            )
            self.client_socket.connect((self.address["host"], self.address["port"]))
        else:
            self.client_socket.connect(
                (self.address['host'], self.address['port']))

        print(f"\nConnection created with: {self.address['host']}:{self.address['port']}\n")

        try:
            # send the query
            print(
                f'Sending GET request to {self.address["host"]}:{self.address["port"]} ...'
            )

            self.request = self.create_get_request()
            self.client_socket.sendall(self.request)

            # timeout to receive data completely
            response_raw = b''
            self.client_socket.settimeout(0.5)
            # read the response
            # getting full response from buffer then tokenizing it
            # response is a dictionary with all headers and content
            while True:
                try:
                    response_raw_temp = self.client_socket.recv(self.buffer_size)
                    response_raw += response_raw_temp
                except:
                    break

            self.response = self.tokenize_response(response_raw)
            self.response_decode()

            print(f"Response : {self.response['status']} {self.response['status_code']}")
            print('Content-Length :', len(self.response["content"]))

        finally:
            self.client_socket.close()
            print('\nClient socket closed')

        # saving a temp.html file of response content for testing purposes
        with open('temp.html', 'w+') as html_file:
            html_file.write(self.response['content'])
        return self.response

    def response_decode(self):
        content = self.response['content']
        mime = magic.from_buffer(content, mime=True)
        self.response['content'] = self.response['content'].decode("utf-8", "ignore")

    def tokenize_address(self, address):
        address_dict = {}

        # adding http if no protocol to get urlsplit working correctly
        if "http" not in address or "https" not in address:
            address = 'http://' + address

        parsed = urlsplit(address)
        print(address)
        address_dict['protocol'] = parsed.scheme
        address_dict['host'] = parsed.hostname
        address_dict['port'] = parsed.port
        address_dict['path'] = parsed.path

        if address_dict['host'] is None:
            raise Exception('Invalid Host')

        if address_dict['port'] is None:
            if address_dict['protocol'] == 'https':
                address_dict['port'] = 443
            else:
                address_dict['port'] = 80

        if address_dict['path'] == '':
            address_dict['path'] = '/'

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
    # client.send_request('127.0.0.1:1234/files/test.jpg')
    client.send_request('google.com')
    # client.send_request('https://www.google.com:443')
    # client.send_request('http://youtube.com')
    # client.send_request('https://vce.umz.ac.ir/samaweb/Login.aspx')
