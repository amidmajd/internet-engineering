import socket
import time
import os
import magic


class ServerError(Exception):
    # custom exception for server
    def __init__(self, status, message=None):
        self.status = status
        self.message = str(message)

    def __str__(self):
        if self.message:
            return f'ServerError, {self.status} {self.message} '
        else:
            return f'ServerError status code: {self.status}'


class Server:
    # here you can map your files and urls as routes variable
    # using this makes client be able to request for a shorted url and not the exact file
    # you can add anyfile here , struct is like:
    # "URL after site name" : "file relative address"
    routes = {
        '/': 'docs/index.html',
        '/test_img': 'docs/test.jpg'
    }

    buffer_size = None
    server_connection_count = None
    server_address = None
    base_dir = None
    status_code = None
    client_socket = None
    client_address = None
    request = None
    response = None
    file = None
    path = None

    def __init__(self, ip, port, buff_size=4096, c_count=1):
        # c_count is connections count
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.server_address = (str(ip), int(port))
        self.buffer_size = int(buff_size)
        self.server_connections = int(c_count)
        # initiating a socket for server in TCP/IPv4 and given port and making the port reuseable
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(self.server_connections)

    def __del__(self):
        self.server_socket.close()
        print('\nServer socket closed')

    def run(self):
        while True:
            print(
                f'\n\nWaiting for requests on {self.server_address[0]}:{self.server_address[1]} ...')
            # Wait for an incomming connection and accept
            self.client_socket, self.client_address = self.server_socket.accept()
            print('Connection accepted from:', self.client_address)
            try:
                while True:
                    print()
                    try:
                        # read the request
                        # getting full request from buffer then tokenizing it
                        # request is a dictionary with all headrs and content
                        request_raw = self.client_socket.recv(
                            self.buffer_size).decode('utf-8')
                        # print(request_raw)
                        if request_raw:
                            self.request = self.tokenize_request(request_raw)
                            print(
                                f'Request : {self.request["method"]} {self.request["url"]}')
                            # loading file in memory (because this is a small test server)
                            # this way server doesnt need to open and close file everytime
                            self.file, self.path = self.url_manager()
                            # creating responses and handling each method
                            if self.request['method'] == 'GET':
                                self.response = self.create_get_response()
                            else:
                                raise ServerError(501)
                        else:
                            break
                    except ServerError as e:
                        # handling errors in server with custom exception class
                        # and setting status code of error as server response status code
                        # then creating suitable response for error
                        self.status_code = int(e.status)
                        self.response = self.create_get_response()
                        print('SERVER ERROR :', e.status, e.message)
                    # sending response to client
                    self.client_socket.sendall(self.response)
                    print(
                        f'Response: {self.status_code} {self.request["method"]} {self.request["url"]}')
                    print()
            except Exception as e:
                print('SERVER ERROR :', e)
            finally:
                self.client_socket.close()
                print('Client socket closed')

    def tokenize_request(self, request):
        request_dict = {'method': '---', 'url': '/'}
        try:
            # spliting request data to lines
            tags = request.split('\r')
            first_tag, tags = tags[0], tags[1:]
            # spliting first line=> method, url, protocol & version
            tmp = first_tag.split(' ')
            request_dict['method'] = tmp[0]
            request_dict['url'] = tmp[1]
            request_dict['protocol'], request_dict['version'] = tmp[2].split(
                '/')

            # data after first line :
            for i, tag in enumerate(tags):
                # getting rid of \n in the left side of lines and spiliting them to tag : value
                tmp = tag.lstrip().rstrip().split(': ')

                # if and empty line exists in request tags it means next(last) tag is the content
                request_dict['content'] = ''
                if tmp[0] == '' and i != 0:
                    request_dict['content'] = tags[-1].lstrip().rstrip()
                    break
                else:
                    request_dict[tmp[0]] = tmp[1]
            return request_dict
        except Exception as e:
            # bad request structure
            self.request = request_dict
            raise ServerError(400, e)

    def content_type(self, file):
        # for this function to work you would need to install magic library
        # pip install python-magic
        # returns extension or mime (html content type)
        # using files magic number not extension
        mime = magic.from_buffer(file, mime=True)
        return mime
        # here is an old way to do this with limited extensions:
        # if path.endswith(".html") or path.endswith(".txt")
        #     return "text/html"
        # elif path.endswith(".png")
        #     return "image/png"
        # elif path.endswith(".jpg") or path.endswith(".jpeg")
        #     return "image/jpeg"
        # else:
        #     return "application/octet-stream"

    def status_text(self):
        known_status = {
            200: 'OK',
            300: '300',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error',
            501: 'Not Implemented',
        }
        return known_status[self.status_code]

    def create_content(self):
        # output content is binary encoded
        content = ''
        # if till here status code is 200 then content is requested file
        if self.status_code == 200:
            # files are loaded as binary so they dont need encoding
            content = self.file
        else:
            # if we have some other status codes then error content html:
            content = '\n'.join((
                '<html>',
                '    <header>',
                f'        <title>{self.status_code} - {self.status_text()}</title>',
                '    </header>',
                '    <body>',
                '        <br><br>',
                f'        <h1 style="text-align:center; font-size:100px">{self.status_code}</h1>',
                f'        <h2 style="text-align:center; font-size:80px">{self.status_text()}</h2>',
                '    </body>',
                '</html>',
            )).rstrip().lstrip().encode('utf-8')    # removing \n from content sides then encoding it
        return content

    def url_mapper(self, url):
        # returns destination url as relative path
        new_url = self.routes.get(url)
        # if new_url is not None return it otherwise return given url
        # if input url is our real url then deleting first / in the start of it
        return new_url or url[1:]

    def url_manager(self):
        # reading file as a binary object and returning it with the path
        file = b''
        path = self.request['url']
        try:
            # getting right the file url then absolute path of it
            url_path = self.url_mapper(self.request['url'])
            path = os.path.join(self.base_dir, url_path)
            with open(path, 'rb') as f:
                file = f.read()
            self.status_code = 200
        except Exception as e:
            # file did not found!
            self.status_code = 404
        return file, path

    def create_get_response(self):
        content = self.create_content()
        content_type = self.content_type(content)

        response = '\n'.join((
            f"HTTP/1.1 {self.status_code} {self.status_text()}",
            f"Date: {time.ctime()}",
            f"Content-Type: {content_type}",
            f"Content-Length: {len(content)}",
        ))
        response = response.lstrip().rstrip().encode('utf-8') + b"\r\n\r\n" + content
        # removing \n from response sides and encoding the response to binary
        return response


if __name__ == '__main__':
    server = Server('127.0.0.1', 1234)  # create the server with ip:port
    server.run()
