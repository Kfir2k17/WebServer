import socket
import os
import urllib.parse

class Server: # Class that handles the socket
    def __init__(self): # Constructor
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = None

    def send(self, message): # Sends a message to the client
        self.client_socket.send(message)

    def recv(self, amount): # Recieves ceratin amount of bytes
        return self.client_socket.recv(amount)

    def start_server(self): # creates the server client
        self.server_socket.bind(("127.0.0.1", 80))
        self.server_socket.listen()

    def stop_server(self): # stops the server client
        self.server_socket.close()

    def start_client(self): # start the client
        self.client_socket, address = self.server_socket.accept()

    def stop_client(self): # stop the client
        self.client_socket.close()

class Response: # The class that handles with the HTTP responses
    def __init__(self, path):
        self.code = "" # The status code of the repsponse
        self.file_type = "" # The type of the file
        self.path = path # The path to the file

        self.body = self.get_body() # The body of the response (information that's being transferred)
        self.headers = self.create_headers() # The headers of the response

        self.msg = self.headers.encode("utf-8") + self.body

    def check_file(self): # Checks if the path is right and sets the parmaters
        if not os.path.isfile(self.path):
            self.code = "404 NOT FOUND"
            self.file_type = "text/plain"
            self.body = "Connection: close\r\n\r\n404 Not Found"
            return False

        self.code = "200 OK"
        self.file_type = self.get_type()
        return True

    def create_headers(self): # Accepts and sends the bodyrmation the client requested
        headers = f"HTTP/1.1 {self.code} \r\n"
        headers += f"Content-Type: {self.file_type} \r\n"
        headers += f"Content-Length: {len(self.body)} \r\n"
        headers += "\r\n"
        return headers

    def get_type(self): # Returns the type of the file
            file_type = self.path.split(".")[-1]
            if file_type == "html":
                return "text/html"
            elif file_type == "css":
                return "text/css"
            elif file_type == "js":
                return "application/javascript"
            elif file_type == "jpg":
                return "image/jpeg"
            elif file_type == "gif":
                return "image/gif"
            elif file_type == "png":
                return "image/png"
            elif file_type == "ico":
                return "image/x-icon"

            return ""

    def get_body(self): # Sets the body of the file
        if self.check_file():
            file = open(self.path, 'rb')

            body = file.read()
            file.close()
            return body

class Request: # A class handling the HTTP requests
    def __init__(self, server): # Constructor
        self.server = server
        self.data = self.recv_request()

        self.path = ""
        if not self.data == "":
            self.process_request()
            self.path = self.get_path()


    def recv_request(self): # checks if the request is empty, and gets the initial 4 bytes if not
        data = self.server.recv(4)
        if not data: # Checks if the browser is done requesting
            return ""
        return data.decode("utf-8")

    def process_request(self): # "Takes" all the data
        while not self.data.endswith("\r\n\r\n"):
            self.data += self.server.recv(1).decode("utf-8")

    def get_path(self): # Returns the path of the requested file
        path = self.data.split(' ', 2)[1].replace("+", " ")
        path = urllib.parse.unquote(path)
        path = path[1:]

        return path


def main(): # The main block of code
    os.chdir("webroot")
    server = Server()
    server.start_server()

    while True:
        server.start_client()
        req = Request(server)

        if req.data == '':  # No more data (client has nothing left to send)
            print("No more requests from client.")
            break  # Exit the loop as the client has finished sending data

        print(req.data)
        r = Response(req.path) # Creating the response
        server.send(r.msg)

        server.stop_client()

    """
    # A
    response = "HTTP/1.1 200 OK \r\nContent-Type: text/html\r\nContent-Length: 3\r\n\r\n hi!".encode()

    # B
    response = "HTTP/1.1 200 OK \r\nContent-Type: text/html\r\nContent-Length: 87\r\n\r\n<html><head></head><body><a href='http://www.google.com'>Go To Google</a></body></html>.encode()"

    # C
    index = Response("index.html")
    server.send(index.msg)
    """

    os.chdir("..")
    server.stop_client()

main() # Call of the main function