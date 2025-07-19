from websocket_server import WebsocketServer
import json

class TheBehavior:
    def __init__(self, client, server):
        self.client = client
        self.server = server

    def send_message(self, data: dict):
        self.server.send_message(self.client, json.dumps(data))


class WebSocketStuff:
    initialized = False
    clients = {}

    @staticmethod
    def initialize_socket():
        if WebSocketStuff.initialized:
            return

        def on_message(client, server, message):
            try:
                data = json.loads(message)
                if data.get("command") == "injected" and data.get("value") not in WebSocketStuff.clients:
                    from seliware import Seliware
                    Seliware.on_injected()
                    WebSocketStuff.clients[data["value"]] = TheBehavior(client, server)
            except Exception:
                pass

        def on_disconnect(client, server):
            to_remove = [k for k, v in WebSocketStuff.clients.items() if v.client['id'] == client['id']]
            for key in to_remove:
                del WebSocketStuff.clients[key]

        server = WebsocketServer(port=3000, host='127.0.0.1')
        server.set_fn_message_received(on_message)
        server.set_fn_client_left(on_disconnect)

        from threading import Thread
        Thread(target=server.run_forever, daemon=True).start()

        WebSocketStuff.initialized = True
