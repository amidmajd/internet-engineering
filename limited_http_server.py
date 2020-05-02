import socket
import filetype
import time
import os
import magic


class server:
    base_dir = None
    status_code = None
    buffer_size = 100
    server_address = None
    client_socket = None
    client_address = None
    request = None
    response = None
    file = None
    path = None

    def __init__(self, ip, port):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.server_address = (str(ip), int(port))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(10)

    def __del__(self):
        self.server_socket.close()
        print('\nserver socket closed')

    def run(self):
        while True:
            try:
                print('\nwaiting for request ...')
                # Wait for an incomming connection and accept
                self.client_socket, self.client_address = self.server_socket.accept()
                print('\nconnection accepted from:', self.client_address, '\n')

                # read the request
                # getting full request from buffer then tokenizing it
                # request is a dictionary with all headrs and content
                request_raw = self.get_from_buffer()
                if request_raw:
                    # print(request_raw)
                    self.request = self.tokenize_request(request_raw)
                    print(f'Request : {self.request["method"]} {self.request["url"]}\n')
                    self.file, self.path = self.url_manager()
                    # answering the request
                    self.response = self.create_response()
                    self.client_socket.sendall(self.response)
                    print(f'\nResponse: {self.status_code} {self.request["method"]} {self.request["url"]}')

                    # try:
                    #     print(self.response.decode('utf-8'))
                    # except:
                    #     print(self.response)
            finally:
                self.client_socket.close()
                print('\nclient socket closed')

    def get_from_buffer(self):
        data = b''
        while True:
            buff = self.client_socket.recv(self.buffer_size)
            # get data from buffer object until it is empty
            data += buff
            if len(buff) < self.buffer_size:
                break
        return data.decode('utf-8')

    def tokenize_request(self, request):
        request_dict = {}
        # spliting request data to lines
        tags = request.split('\r')
        first_tag, tags = tags[0], tags[1:]
        # spliting first line=> method, url, protocol & version
        tmp = first_tag.split(' ')
        request_dict['method'] = tmp[0]
        request_dict['url'] = tmp[1]
        request_dict['protocol'], request_dict['version'] = tmp[2].split('/')

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

    def content_type(self, file):
        # need to install magic library
        # returns extension or mime (html content type)
        # uses files magic number not extension
        return magic.from_buffer(file, mime=True)
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
            502: 'Bad Gateway'
        }
        return known_status[self.status_code]

    def create_content(self):
        content = ''
        if self.status_code == 200:
            content = self.file
        else:
            # if we have some other status code the error page:
            # and removing \n from content sides then encoding it
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
            )).rstrip().lstrip().encode('utf-8')
        return content

    def url_mapper(self, url):
        known_map = {
            '/': 'docs/index.html',
        }
        new_url = known_map.get(url)
        # if new_url is not None return it otherwise return given url
        # if input url is our real url then deleting first / in the start of it
        return new_url or url[1:]

    def url_manager(self):
        file = b''
        path = self.request['url']
        try:
            url_path = self.url_mapper(self.request['url'])
            path = os.path.join(self.base_dir, url_path)
            with open(path, 'rb') as f:
                file = f.read()
            self.status_code = 200
        except Exception as e:
            self.status_code = 400
        return file, path

    def create_response(self):
        content = self.create_content()
        content_type = self.content_type(content)
        response = '\n'.join((
            f"HTTP/1.1 {self.status_code} {self.status_text()}",
            f"Date: {time.ctime()}",
            f"Content-Type: {content_type}",
            f"Content-Length: {len(content)}",
        ))
        response = response.lstrip().rstrip().encode('utf-8') + b'\n\n' + content
        # removing \n from response sides
        return response


if __name__ == '__main__':
    server = server('127.0.0.1', 8080)
    server.run()
