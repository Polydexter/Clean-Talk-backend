from channels.generic.websocket import JsonWebsocketConsumer

class ChatConsumer(JsonWebsocketConsumer):
    #groups = [???]

    def connect(self):
        self.accept()
        print("Connected")

    def receive_json(self, content):
        print(content)

    def send_json(self, content):
        pass

    def disconnect(self, close_code):
        print('Disconnected: ', close_code)
