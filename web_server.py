import socket
def create_response(html, code): # creats a code to return to the client
    html_l = len(html)
    resposne = f"HTTP/1.1 200 OK \r\n Content-Type: text/html\r\n Content-Length: {html_l}\r\n\r\n" + html
    return resposne

def main(): # Starts the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 80))
    server_socket.listen()
    client_socket, address = server_socket.accept()

    client_socket.recv(1024)

    # A
    response = create_response("kfir carmeli haloser")

    # B

    client_socket.send(response.encode())

    server_socket.close()
    client_socket.close()


main() # The call of the main function