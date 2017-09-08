import websockets
import collections
import asyncio
import json

from fatal import fatal

class SlaveServer(object):

    MASTER_HOST = 'localhost'
    MASTER_PORT = 6000
    ALIAS = 'alias'

    def __init__(self):
        self.master_websocket = None
        self.master_server_url = None
        self.send_data = False
        

    
    
    @asyncio.coroutine
    def handler(self):
        master_server_url = 'ws://%s:%s/' % (self.MASTER_HOST, self.MASTER_PORT)
        self.master_websocket = yield from websockets.connect(
            master_server_url
        )
        consumer_task = asyncio.ensure_future(self.process_masterslave_interaction())
        producer_task = asyncio.ensure_future(self.receive_from_master())
        done, pending = yield from  asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

    @asyncio.coroutine
    def process_masterslave_interaction(self):
        while True:
            if self.send_data:
                yield from self.master_websocket.send('hi ' + self.ALIAS)
    
    @asyncio.coroutine
    def receive_from_master(self):
        while True:
            rec = yield from self.master_websocket.recv()
            print('>> ', rec)
    
    def run_slave(self):
        asyncio.get_event_loop().run_until_complete(self.handler())

if __name__ == '__main__':
    slave_server = SlaveServer()
    slave_server.run_slave()