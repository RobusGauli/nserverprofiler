
import asyncio
import websockets
import json

from fatal import fatal


class MasterServer(object):
    '''Should be compatible with 3.4 /3.5 ad + '''
    
    MASTER_HOST = 'localhost'
    MASTER_PORT = 6000

    COMMAND_RESUME = 'resume'

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
            msg = yield from self.current_slave.recv()
            yield from asyncio.sleep(2)
            print(msg, 'g')
    
    @asyncio.coroutine 
    def master_sender(self, websocket):
        '''I should be able to send the command to the current slave to perform the certain action'''
        print('yeah')
        while True:
            yield from self._send_command(self.COMMAND_RESUME)
            
    
    @asyncio.coroutine
    def _handler(self, websocket, path):
        slave_socket = SlaveSocket(websocket)
        self.slaves.add(slave_socket)
        #let this be a current_slave
        self.current_slave = slave_socket
        self.current_slave.send_data = True
        
        master_consumer_task = asyncio.ensure_future(self.master_consumer(websocket))
        master_sender_task = asyncio.ensure_future(self.master_sender(websocket))
        _, pending = yield from asyncio.wait(
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



class SlaveSocket(object):

    def __init__(self, slave_socket):
        self.slave_socket = slave_socket
        self.send_data = False
    
    def send(self, data):
        yield from self.slave_socket.send(data)
    
    def recv(self):
        msg = yield from self.slave_socket.recv()
        return msg
if __name__ == '__main__':
    master_server = MasterServer()
    master_server.run_master()

