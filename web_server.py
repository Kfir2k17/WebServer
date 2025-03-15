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
        self.data = self.recv_request() # Collect the four bytes of the request

        self.request_type = self.check_request_type() # The type of the request (GET/POST)

        self.path = b"" # The path to the file/Where the file will be created (if POST), will be filled later
        if not self.data == b"": # Checks if the request is not empty
            self.process_request() # Fills the full data that was returned. if there was problem, it will be handled in the response
            self.path = self.get_path() # Fills the field based on the data recieved


    def recv_request(self): # checks if the request is empty, and gets the initial 4 bytes if not
        data = self.server.recv(4)
        if not data: # Checks if the browser is done requesting
            return b""
        return data

    def check_request_type(self):
        if self.data[:3] == b"GET" or len(self.data) == 3:
            return "GET"
        return "POST"


    def process_request(self): # Processes the request and handles error (if the transsition stops)
        while not self.data.endswith(b"\r\n\r\n"):  # Read headers first
            chunk = self.server.recv(1)
            if not chunk:
                self.path = b""
                self.data = b""
                break
            else:
                self.data += chunk

        if self.request_type == "POST":
            # Extract Content-Length
            headers = self.data.split(b"\r\n")
            content_length = 0
            for header in headers:
                if header.lower().startswith(b"content-length:"):
                    content_length = int(header.split(b":")[1].strip())
                    break

            self.data = self.data + self.server.recv(content_length)  # Collect the file_data of the POST, and adds it to the file

    def get_path(self): # Returns the path of the requested file
        if self.data == '': # Checks if there was an error in the recieving process
            return ''

        str_data = str(self.data)
        path = str_data.split(' ', 2)[1].replace("+", " ")
        path = urllib.parse.unquote(path)
        path = path[1:]

        return path

class Response: # The class that handles with the HTTP responses
    def __init__(self, path, request_type, data): # Constructor for get
        self.code = "" # The status code of the response
        self.file_type = "" # The type of the file
        self.path = path # The path to the file

        self.request_type = request_type # The type of the request (POST/GET)

        self.data = data # For POST, the data that needs to be downloaded

        self.body = b""
        self.set_body() # The body of the response (information that's being transferred)

        self.headers = self.create_headers() # Creates the headers of the response

        self.msg = self.headers.encode() + self.body # The final text that will be sent to the client

    def set_body(self): # Sets the body of the file
        if self.request_type == "POST":
            if self.check_file():
                self.save_image() # Creates the file on the computer


        if self.request_type == "GET":
            if self.check_file(): # If the request is GET to a file, copies the data to the body which will be sent
                file = open(self.path, 'rb')

                self.body = file.read()
                file.close()


    def set_status(self, status): # Sets the status of the code that will be returned
        if status == CODE_NOT_FOUND:
            self.code = CODE_NOT_FOUND
            self.file_type = MIME_TYPES["txt"]
            self.body = ("Connection: close\r\n\r\n" + CODE_NOT_FOUND).encode()

        if status == CODE_OK:
            self.code = CODE_OK

        if status == CODE_CREATED:
            self.body = CODE_CREATED.encode()
            self.code = CODE_CREATED
            self.file_type = MIME_TYPES["txt"]

        if status == CODE_INTERNAL_SERVER:
            self.code = CODE_INTERNAL_SERVER
            self.file_type = MIME_TYPES["txt"]
            self.body = ("Connection: close\r\n\r\n" + CODE_INTERNAL_SERVER).encode()


    def check_file(self): # Checks if the path is right and handles different errors
        if self.path == "": # Checks if the response was empty
            self.set_status(CODE_INTERNAL_SERVER)
            return False

        if self.request_type == "POST": # If the request was post, treat differently
            self.set_status(CODE_CREATED)
            return True

        elif not os.path.isfile(self.path) and self.request_type == "GET":
            if "calculate_next" in self.path or "calculate-next" in self.path: # Checks if the path presented was a function
                self.body = calculate_next(self.path).encode()
                self.set_status(CODE_OK)
                self.file_type = MIME_TYPES["txt"]

                if self.body == "": # Checks if there's problem
                    self.set_status(CODE_INTERNAL_SERVER)

                return False

            if "calculate_area" in self.path or "calculate-area" in self.path: # Checks if the path presented was a function
                self.body = calculate_area(self.path).encode()
                self.set_status(CODE_OK)
                self.file_type = MIME_TYPES["txt"]

                if self.body == "":
                    self.set_status(CODE_INTERNAL_SERVER)

                return False

            if "?image-name=" in self.path: # For handling request for an image (4.11)
                self.path = self.path.split("?image-name=", 1)[-1]

                if not os.path.isfile(self.path): # Checks if the file exists
                        if os.path.isfile("upload/" + self.path): # Checks if the file exists in upload
                            self.path = "upload/" + self.path

                        elif os.path.isfile("imgs/" + self.path): # Checks if the file exists in imgs directory
                            self.path = "imgs/" + self.path

                        else:
                            self.set_status(CODE_NOT_FOUND)
                            return False

            else: # Returns that the file was not
                self.set_status(CODE_OK)
                return False

        # If the code is okay
        self.set_status(CODE_OK)
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

        except KeyError: # If the mime provided does not exist
            self.set_status(CODE_INTERNAL_SERVER)
            return ""

    def save_image(self): # Takes the data from the POST request, and creates the file
        parts = self.data.split(b"\r\n\r\n")
        boundary = parts[1] # The second header
        file_data = parts[2] # The data of the file which is being transmissioned

        if not os.path.isdir(self.path): # Checks if the path leads to an existing directory, creates new one if not
            os.mkdir(self.path)

        name = boundary.split(b"filename=\"",1)[-1].split(b"\"",1)[0].decode() # Gets the name of the picture
        f = open(self.path + "/" + name, "wb")
        f.write(file_data) # Writes the data to a file
        f.close()


def calculate_next(file_path): # Returns the following number of the parameter that was passed, 4.5/6
    num = int(file_path.split("num=")[-1])
    num += 1
    return str(num)

def calculate_area(file_path): # Returns the area of the triangle. 4.9
    content_type = MIME_TYPES["txt"]
    param = file_path.split("?",1)[-1]
    params = param.split("&")

    if len(params) == 2:
        # check if height and width are negative

        height = int(params[0].split("=")[-1])
        width = int(params[1].split("=")[-1])

        if height < 0 or width < 0:
            return ""

        data = str(0.5*height*width)
    else:
        data = "" # If there's problem

    return data


def main(): # The main block of code
    os.chdir("webroot")
    server = Server()
    server.start_server()

    while True: # Turns on the server
        server.start_client()
        request = Request(server)

        # print(request.data)

        print(request.data)
        if not request.request_type == "GET":
            response = Response(request.path, request.request_type, request.data) # Creating the response

        else:
            response = Response(request.path, request.request_type, b"")  # Creating the response

        print(response.code)
        server.send(response.msg)

        server.stop_client()
        if response.code == CODE_NOT_FOUND or response.code == CODE_INTERNAL_SERVER: # Closes the server in the occasion of an error
            break

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
    server.stop_server()

main() # Call of the main function