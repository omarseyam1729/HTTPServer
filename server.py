import socket
import threading

class HTTPServer:
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.routes = {} 
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
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
        try:
            # Parse the request line
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
        return 'HTTP/1.1 404 Not Found\r\n\r\n404 Not Found'

    def internal_error_response(self):
        return 'HTTP/1.1 500 Internal Server Error\r\n\r\n500 Internal Server Error'

    def add_route(self, method, path, handler):
        self.routes[(method, path)] = handler

# Define handler functions
def index():
    return 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Welcome to the Home Page</h1>'

def about():
    return 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>About Us</h1><p>This is the about page.</p>'

def not_found():
    return 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>'

if __name__ == '__main__':
    server = HTTPServer(host='localhost', port=8000)
    server.add_route('GET', '/', index)
    server.add_route('GET', '/about', about)
    server.start()
