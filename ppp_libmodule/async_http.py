import asyncore

from .http import HttpRequestHandler

class Handler(asyncore.dispatcher_with_send):
    def __init__(self, class_, sock):
        super().__init__(sock)
        self._class = class_
        self.in_buffer = b''
        self.out_buffer = None
        self.headers = None
        self.content_length = None
        self.generator = None

    def start_response(self, status, headers):
        """Function passed to the HttpRequestHandler."""
        assert self.out_buffer is None, \
                'start_response called after data was returned.'
        pred = ''.join(['\r\n%s:%s' % x for x in headers])
        self.out_buffer = (status+headers).encode()

    def handle_read(self):
        self.in_buffer += self.recv(8192)
        if len(self.in_buffer) >= 2**23:
            # More than 8MB headers, seriously?
            self.send('413 Request Entity Too Large\r\n')
        if not self.headers and b'\r\n\r\n' in self.in_buffer:
            (headers_buff, self.in_buffer) = self.in_buffer.split(b'\r\n\r\n')
            self.on_headers_end(headers_buff.decode().split('\r\n'))
        elif self.headers and len(self.in_buffer) >= self.content_length:
            self.on_content_end(self.in_buffer)
            self.in_buffer = None

    def on_headers_end(self, headers):
        self.method = headers[0].split(' ', 1)[1]
        self.headers = dict(map(lambda x:x.split(': ', 1), headers[1:]))
        self.content_length = int(self.headers.get('Content-Length', '0'))

    def on_content_end(self, content):
        request = Request.from_json(content.decode())
        print(repr(request))
        self.generator = iter(self._class(request).answer())

    def handle_write(self):
        print(self.generator)
        print(self.out_buffer)
        if not self.generator and not self.out_buffer:
            return
        if not self.out_buffer:
            try:
                item = next(self.generator)
            except StopIteration:
                self.generator = None
            else:
                self.out_buffer += item.as_json().encode()

        sent = self.send(self.out_buffer)
        self.out_buffer = self.out_buffer[sent:]

class Router(asyncore.dispatcher):
    def __init__(self, host, port, class_):
        super().__init__()
        self.class_ = class_
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        print('Incoming connection from %s' % repr(addr))
        handler = Handler(self.class_, sock)
