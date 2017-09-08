
import asyncio
import websockets
import json

from fatal import fatal


class MasterServer(object):
    '''Should be compatible with 3.4 /3.5 ad + '''
    
    MASTER_HOST = 'localhost'
    MASTER_PORT = 6000

    def __init__(self):
        self.current_slave = None
        self.slaves = set()
    
    def _send_command(self, data):
        try:
            yield from self.current_slave.send(data)
        except websockets.exceptions.ConnectionClosed:
            fatal('Connection closed to the current_running slave')

    @asyncio.coroutine
    def master_consumer(self, websocket):
        '''I should be able to receive the the data from the just single websocket at any given time'''
        while True:
            yield from websocket.send('master')

    @asyncio.coroutine 
    def master_sender(self, websocket):
        '''I should be able to send the command to the slave to perform the certain action'''
        print('yeah')
        while True:
            msg = yield from websocket.recv()
            print(msg, 'g')
    
    @asyncio.coroutine
    def _handler(self, websocket, path):
        self.slaves.add(websocket)
        #let this be a current_slave
        self.current_slave = websocket
        master_consumer_task = asyncio.ensure_future(self.master_consumer(websocket))
        master_sender_task = asyncio.ensure_future(self.master_sender(websocket))
        done, pending = yield from asyncio.wait(
            [master_consumer_task, master_sender_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
    
    def run_master(self):
        '''Master server'''
        _master_server = websockets.serve(
            self._handler,
            self.MASTER_HOST,
            self.MASTER_PORT
        )
        asyncio.get_event_loop().run_until_complete(_master_server)
        asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    master_server = MasterServer()
    master_server.run_master()

