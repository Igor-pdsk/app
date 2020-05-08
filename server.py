"""
Серверное приложение для соединений
"""
import asyncio
from asyncio import transports


class ClientProtocol(asyncio.Protocol):
    login: str
    server: 'Server'
    transport: transports.Transport
    mess = ['\r\n', '\r\n', '\r\n', '\r\n', '\r\n', '\r\n', '\r\n', '\r\n', '\r\n', '\r\n']

    def __init__(self, server: 'Server'):
        self.server = server
        self.login = None

    def data_received(self, data: bytes):
        decoded = data.decode()
        self.mess[9] = self.mess[8]
        self.mess[8] = self.mess[7]
        self.mess[7] = self.mess[6]
        self.mess[6] = self.mess[5]
        self.mess[5] = self.mess[4]
        self.mess[4] = self.mess[3]
        self.mess[3] = self.mess[2]
        self.mess[2] = self.mess[1]
        self.mess[1] = self.mess[0]
        self.mess[0] = decoded + '\r\n'

        #print(decoded)

        if self.login is None:
            # login:User
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "").replace("\r\n", "")
                self.transport.write(
                    f"Привет, {self.login}!".encode()
                )
                self.transport.write(self.mess[9].encode())
                self.transport.write(self.mess[8].encode())
                self.transport.write(self.mess[7].encode())
                self.transport.write(self.mess[6].encode())
                self.transport.write(self.mess[5].encode())
                self.transport.write(self.mess[4].encode())
                self.transport.write(self.mess[3].encode())
                self.transport.write(self.mess[2].encode())
                self.transport.write(self.mess[1].encode())
                self.transport.write(self.mess[0].encode())
        else:
            self.send_message(decoded)
        print(self.login+":"+decoded)
        #------------------
        for client in self.server.clients:
            num=0
            for client1 in self.server.clients:
                if client.login == client1.login:
                    num = num + 1
            if (num == 2):
                if self.login == client.login:
                    self.server.clients.remove(self)
                    print("Соединение разорвано")
        # ------------------

    def send_message(self, message):
        format_string = f"<{self.login}> {message}"
        encoded = format_string.encode()

        for client in self.server.clients:
            if client.login != self.login:
                client.transport.write(encoded)

    def connection_made(self, transport: transports.Transport):
        self.transport = transport
        self.server.clients.append(self)
        print("Соединение установлено")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("Соединение разорвано")


class Server:
    clients: list

    def __init__(self):
        self.clients = []

    def create_protocol(self):
        return ClientProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.create_protocol,
            "127.0.0.1",
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
