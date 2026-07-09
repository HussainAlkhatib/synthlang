# Network module
@python module "socket" as socket
@python module "requests" as requests

fn tcp_connect(host: str, port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock

fn tcp_listen(port: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    return server

fn tcp_accept(listener) -> tuple:
    conn, addr = listener.accept()
    return (conn, addr)

fn udp_send(host: str, port: int, data: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data.encode(), (host, port))

fn udp_receive(port: int, size: int) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    data, _ = sock.recvfrom(size)
    return data.decode()

fn http_get(url: str):
    return requests.get(url).text

fn http_post(url: str, data: str):
    return requests.post(url, data=data).text