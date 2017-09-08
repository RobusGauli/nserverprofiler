import websockets
import collections
import asyncio
import json
import argparse

from fatal import fatal

class SlaveServer(object):

    MASTER_HOST = 'localhost'
    MASTER_PORT = 6000
    ALIAS = 'alias'

    def __init__(self, id):
        self.master_websocket = None
        self.master_server_url = None
        self.send_data = True
        self.unique_id = id
        

    
    
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
            # if self.send_data:
            #     yield from self.master_websocket.send('hi ' + self.unique_id)
            yield from asyncio.sleep(1)
    
    @asyncio.coroutine
    def receive_from_master(self):
        count = 1
        while True:
            rec = yield from self.master_websocket.recv()
            count += 1
            if rec == 'resume':
                #change the senddata to True
                print('recived << ', rec)
                print('sending', count)
                yield from self.master_websocket.send('hi ' + self.unique_id)
            else:
                print('paused', count)
                self.send_data = False
            yield from asyncio.sleep(3)
    
    def run_slave(self):
        asyncio.get_event_loop().run_until_complete(self.handler())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', dest='id', type=str)
    args = parser.parse_args()

    slave_server = SlaveServer(args.id)
    slave_server.run_slave()