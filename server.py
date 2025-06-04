import socket
import threading

class HTTPServer:
    """Minimal HTTP/1.0 server supporting basic route handling."""

    def __init__(self, host='localhost', port=8000):
        """Initialize the server instance.

        Parameters
        ----------
        host : str, optional
            Interface to bind the listening socket to.
        port : int, optional
            Port number to listen on.
        """
        self.host = host
        self.port = port
        self.routes = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        """Begin listening for incoming connections and process them."""

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f'Serving HTTP on {self.host} port {self.port}...')
        try:
            while True:
                client_connection, client_address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_connection,)).start()
        except KeyboardInterrupt:
            print('Server is shutting down.')
        finally:
            self.server_socket.close()

    def handle_client(self, client_connection):
        """Process a connected client socket."""

        try:
            request_data = b''
            while True:
                data = client_connection.recv(1024)
                if not data:
                    break
                request_data += data
                if b'\r\n\r\n' in request_data or b'\n\n' in request_data:
                    break
            if not request_data:
                return
            try:
                request_text = request_data.decode('utf-8')
            except UnicodeDecodeError as e:
                print('Received non-UTF-8 data from client.')
                print(f'Decode error: {e}')
                return
            response = self.handle_request(request_text)
            client_connection.sendall(response.encode())
        except Exception as e:
            print(f'Error: {e}')
        finally:
            client_connection.close()

    def handle_request(self, request_data):
        """Parse the HTTP request and invoke the matching route handler."""

        try:
            print(request_data)
            lines = request_data.splitlines()
            if not lines:
                return self.internal_error_response()
            request_line = lines[0]
            method, path, version = request_line.split()
            handler = self.routes.get((method, path), self.default_response)
            return handler()
        except Exception as e:
            print(f'Error handling request: {e}')
            return self.internal_error_response()

    def default_response(self):
        """Return a generic 404 response for undefined routes."""

        return 'HTTP/1.1 404 Not Found\r\n\r\n404 Not Found'

    def internal_error_response(self):
        """Return a 500 response when an exception occurs."""

        return 'HTTP/1.1 500 Internal Server Error\r\n\r\n500 Internal Server Error'

    def add_route(self, method, path, handler):
        """Register a callback to handle a specific HTTP method and path."""

        self.routes[(method, path)] = handler


def index():
    """Return the HTML for the root page."""

    return 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Welcome to the Home Page</h1>'

def about():
    """Return the HTML for the about page."""

    return 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>About Us</h1><p>This is the about page.</p>'

def not_found():
    """Return a simple 404 page."""

    return 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>'

if __name__ == '__main__':
    server = HTTPServer(host='localhost', port=8000)
    server.add_route('GET', '/', index)
    server.add_route('GET', '/about', about)
    server.start()
