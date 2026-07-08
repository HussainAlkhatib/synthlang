@python module "socket" as socket

fn create_socket(family: str, type: str):
    fam = socket.AF_INET if family == "inet" else socket.AF_INET6
    typ = socket.SOCK_STREAM if type == "stream" else socket.SOCK_DGRAM
    return socket.socket(fam, typ)

fn bind(sock, address: tuple):
    return sock.bind(address)

fn listen(sock, backlog: int):
    return sock.listen(backlog)

fn accept(sock):
    return sock.accept()

fn connect(sock, address: tuple):
    return sock.connect(address)

fn send(sock, data: bytes):
    return sock.send(data)

fn receive(sock, buffer_size: int):
    return sock.recv(buffer_size)