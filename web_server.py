import socket
import os
import urllib.parse

# Finals
CODE_NOT_FOUND = "404 NOT FOUND"
CODE_OK = "200 OK" # If the request was processed
CODE_INTERNAL_SERVER = "500 INTERNAL SERVER ERROR" # If the response is empty
CODE_CREATED = "201 CREATED" # If the file that was posted was created


MIME_TYPES = {  "html": "text/html",
                "css": "text/css",
                "js": "application/javascript",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "gif": "image/gif",
                "png": "image/png",
                "ico": "image/x-icon",
                "txt": "text/plain",
               }

class Server: # Class that handles the socket
    def __init__(self): # Constructor
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = None

    def send(self, message): # Sends a message to the client
        self.client_socket.send(message)

    def recv(self, amount): # Receives certain amount of bytes
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

class Request: # A class handling the HTTP requests
    def __init__(self, server): # Constructor
        self.server = server
        self.data = self.recv_request()

        self.request_type = self.check_request_type()

        self.path = ""
        if not self.data == "":
            self.process_request()
            self.path = self.get_path()


    def check_request_type(self):
        if self.data[:3] == "GET" or len(self.data) == 3:
            return "GET"
        return "POST"


    def recv_request(self): # checks if the request is empty, and gets the initial 4 bytes if not
        data = self.server.recv(4)
        if not data: # Checks if the browser is done requesting
            return ""
        return data.decode("utf-8")

    def process_request(self):
        while not self.data.endswith("\r\n\r\n"):  # Read headers first
            chunk = self.server.recv(1)
            if not chunk:
                self.path = ""
                self.data = ""
                break
            else:
                self.data += chunk.decode("utf-8")

        if self.request_type == "POST":
            # Extract Content-Length
            headers = self.data.split("\r\n")
            content_length = 0
            for header in headers:
                if header.lower().startswith("content-length:"):
                    content_length = int(header.split(":")[1].strip())
                    break

            # Read the exact number of bytes specified in Content-Length
            body = b""
            while len(body) < content_length:
                chunk = self.server.recv(min(1024, content_length - len(body)))
                if not chunk:
                    break
                body += chunk

            self.data = self.data.encode("utf-8") + body  # Append the body to request data

    def get_path(self): # Returns the path of the requested file
        path = self.data.split(' ', 2)[1].replace("+", " ")
        path = urllib.parse.unquote(path)
        path = path[1:]

        return path

class Response: # The class that handles with the HTTP responses
    def __init__(self, path, request_type, data): # Constructor for get
        self.code = "" # The status code of the response
        self.file_type = "" # The type of the file
        self.path = path # The path to the file

        self.request_type = request_type

        self.data = data # For POST, the data that needs to be downloaded

        self.body = bytes()
        self.set_body() # The body of the response (information that's being transferred)

        self.headers = self.create_headers() # The headers of the response

        self.msg = self.headers.encode("utf-8") + self.body # The final text that will be sent to the client

    def check_file(self): # Checks if the path is right and sets the parameters
        if self.path == "": # Checks if the response was empty
            self.code = CODE_INTERNAL_SERVER
            self.file_type = MIME_TYPES["txt"]
            self.body = ("Connection: close\r\n\r\n" + CODE_INTERNAL_SERVER).encode()
            return False

        if self.request_type == "POST":
            self.body = CODE_CREATED
            self.code = CODE_OK
            self.file_type = MIME_TYPES["txt"]
            return True

        elif not os.path.isfile(self.path) and self.request_type == "GET":
            if "calculate_next" in self.path or "calculate-next" in self.path: # Checks if the path presented was a function
                self.body = calculate_next(self.path).encode()
                self.code = CODE_OK
                self.file_type = MIME_TYPES["txt"]
                return False

            if "calculate_area" in self.path or "calculate-area" in self.path: # Checks if the path presented was a function
                self.body = calculate_area(self.path).encode()
                self.code = CODE_OK
                self.file_type = MIME_TYPES["txt"]
                return False

            else: # Returns that the file was not
                self.code = CODE_NOT_FOUND
                self.file_type = MIME_TYPES["txt"]
                self.body = ("Connection: close\r\n\r\n" + CODE_NOT_FOUND).encode()
                return False

        # If the code is okay
        self.code = CODE_OK
        self.file_type = self.get_type()
        return True

    def create_headers(self): # creates the header of the response
        headers = f"HTTP/1.1 {self.code} \r\n"
        headers += f"Content-Type: {self.file_type} \r\n"
        headers += f"Content-Length: {len(self.body)} \r\n"
        headers += "\r\n"
        return headers

    def get_type(self): # Returns the type of the file
        try:
            return MIME_TYPES[self.path.split(".")[-1]]

        except KeyError:
            return ""

    def set_body(self): # Sets the body of the file
        if self.request_type == "POST":
            if self.check_file():
                self.save_image()


        if self.request_type == "GET":
            if self.check_file():
                file = open(self.path, 'rb')

                self.body = file.read()
                file.close()

    def save_image(self): # Takes the data from the POST request, and creates the file
        boundary = self.data.split(b"Content-Type: ")[0].split(b"\r\n")[-1]  # Extract boundary
        parts = self.data.split(boundary)[1:-1]  # Extract only file part
        for part in parts:
            if b"filename=" in part:
                # Extract filename
                name = part.split(b"filename=\"")[1].split(b"\"")[0].decode()
                file_data = part.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n", 1)[0]  # Extract binary content

                f = open(name, "wb")
                f.write(file_data)
                f.close()
                return



def calculate_next(file_path): # Returns the following number of the parameter that was passed, 4.5/6
    num = int(file_path.split("num=")[-1])
    num += 1
    return str(num)

def calculate_area(file_path): # Returns the area of the triangle. 4.9
    content_type = MIME_TYPES["txt"]
    param = file_path.split("?",1)[-1]
    params = param.split("&")

    if len(params) == 2:
        param1 = int(params[0].split("=")[-1])
        param2 = int(params[1].split("=")[-1])
        data = str(0.5*param1*param2)
    else:
        data = ""

    return data


def main(): # The main block of code
    os.chdir("webroot")
    server = Server()
    server.start_server()

    while True: # Turns on the server
        server.start_client()
        request = Request(server)

        # print(request.data)



        if not request.request_type == "GET":
            response = Response(request.path, request.request_type, request.data) # Creating the response

        else:
            response = Response(request.path, request.request_type, "")  # Creating the response

        server.send(response.msg)

        if not response.code == "200 OK" or not response.code == "201 created":
            pass


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