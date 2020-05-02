import socket
import filetype
import time


class server:
    status_code = None
    buffer_size = 100
    server_address = None
    client_socket = None
    client_address = None
    request = None
    response = None

    def __init__(self, ip, port):
        self.server_address = (str(ip), int(port))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(1)

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
                    print(f'Request : {self.request["method"]} {self.request["path"]}')

                    # answering the request
                    self.status_code = 500
                    self.response = self.create_response()
                    self.client_socket.sendall(self.response.encode('utf-8'))
                    print(f'Response: {self.status_code} {self.request["method"]} {self.request["path"]}')

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
        # spliting first line=> method, path, protocol & version
        tmp = first_tag.split(' ')
        request_dict['method'] = tmp[0]
        request_dict['path'] = tmp[1]
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

    def content_type(self):
        return 'text/html'
        # need to install filetype library
        # returns extension or mime (html content type)
        # uses files magic number not extension
        # ftype = filetype.guess(file)
        # if ftype is not None:
        #     return ftype.mime
        # else:
        #     return 'application/octet-stream'
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
            pass
        else:
            # if we have some other status code the error page:
            content = f'''
                <html>
                <header><title>{self.status_code} - {self.status_text()}</title></header>
                <body>
                    </br></br>
                    <h1 style="text-align:center; font-size:100px">{self.status_code}</h1>
                    <h2 style="text-align:center; font-size:80px">{self.status_text()}</h2>
                </body>
                </html>
            '''
        # removing \n from content sides
        return content.rstrip().lstrip()

    def create_response(self):
        content = self.create_content()
        response = f'''
            HTTP/1.1 {self.status_code} {self.status_text}
            Date: {time.ctime()}
            Content-Type: {self.content_type()}
            Content-Length: {len(content)}

            {content}
        '''
        # removing \n from response sides
        return response.rstrip().lstrip()


if __name__ == '__main__':
    server = server('127.0.0.1', 8080)
    server.run()
