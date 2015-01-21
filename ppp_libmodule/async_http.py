import json
import asyncore

from .http import HttpRequestHandler
from ppp_datamodel import Request

class Handler(asyncore.dispatcher_with_send):
    def __init__(self, class_, sock):
        super().__init__(sock)
        self._class = class_
        self._in_buffer = b''
        self._out_buffer = None
        self.headers = None
        self.content_length = None
        self.generator = None

    def start_response(self, status, headers):
        """Function passed to the HttpRequestHandler."""
        assert self._out_buffer is None, \
                'start_response called after data was returned.'
        pred = ''.join(['\r\n%s:%s' % x for x in headers])
        self._out_buffer = (status+headers).encode()

    def handle_read(self):
        self._in_buffer += self.recv(8192)
        if len(self._in_buffer) >= 2**23:
            # More than 8MB headers, seriously?
            self.send('413 Request Entity Too Large\r\n')
            self.close()
        if not self.headers and b'\r\n\r\n' in self._in_buffer:
            (headers_buff, self._in_buffer) = self._in_buffer.split(b'\r\n\r\n')
            self.on_headers_end(headers_buff.decode().split('\r\n'))
        if self.headers and len(self._in_buffer) >= self.content_length:
            content = self._in_buffer
            self._in_buffer = None
            self.on_content_end(content)

    def on_headers_end(self, headers):
        self.method = headers[0].split(' ', 1)[1]
        self.headers = dict(map(lambda x:x.split(': ', 1), headers[1:]))
        self.content_length = int(self.headers.get('Content-Length', '0'))
        if not self.content_length:
            self.on_content_end(None)

    def on_content_end(self, content):
        if content:
            request = Request.from_json(content.decode())
            r = json.dumps(list(self._class(request).answer())).encode()
            self.send(('HTTP/1.0 200 OK\r\nContent-Length: %d\r\n\r\n' % len(r)).encode())
            self.send(r)
        else:
            self.send(b'HTTP/1.0 400 Bad Request\r\n\r\n')
        self.close()

    def handle_close(self):
        print('connection closed.')
        super().handle_close()

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
