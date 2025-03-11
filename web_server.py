import socket
import os

def create_response(info, code, type): # creats a code to return to the client
    info_l = len(info)
    return f"HTTP/1.1 {code} \r\n Content-Type: {type}\r\n Content-Length: {info_l}\r\n\r\n" + info



def send_info(info): # Accepts and sends the information the client requested
    if not os.path.isfile(path):
            return error_404()

    create_response(info, "200 OK", type)


def get_type(path): # Returns the type of the file
        file_type = path.split(".")[-1]
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

def error_404(): # returns 404 error
    return create_response("", "404 Not Found")


def send_file(path):
    if not os.path.isfile(path):
            return error_404()

    file = open(path)
    info = ""
    for line in file:
        info += line

    file.close()
    return create_response(info, "200 OK")


def main(): # Starts the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 80))
    server_socket.listen()
    client_socket, address = server_socket.accept() # Creates the server

    client_socket.recv(1024)

    # A
    # response = create_response_info("hi!")

    # B
    # response = send_info("<html><head></head><body><a href='http://www.google.com'>Go To Google</a></body></html>")

    # C
    # response = send_file("index.html")

    client_socket.send(response.encode())

    server_socket.close()
    client_socket.close()


main() # The call of the main function