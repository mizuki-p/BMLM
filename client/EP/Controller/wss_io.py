# import msgpack as pickle
import umsgpack as pickle
from typing import Tuple

import json
import websockets
from ..configs import Config

class wss_io:
    def __init__(self):
        self.sio = None
    
    async def init(self):
        # await self.sio.connect(Config.API_BASE, transports=['websocket'])
        self.sio = await websockets.connect(Config.API_BASE)
    
    async def register(self, client_id, env_id, scene_name) -> Tuple[bool, str]:
        if self.sio is None:
            return False, 'Websocket not connected'

        try: 
            data = pickle.packb({
                'action': 'register_client',
                'data': {
                    'client_id': client_id,
                    'env_id': env_id,
                    'env_name': scene_name
                }
            })
            print(data)
            # response = await self.sio.call('message', data, namespace='/', timeout=10)
            await self.sio.send(data)
            response = await self.sio.recv()
            response = json.loads(response)
            print(f'Response: {response} (type: {type(response)})')
        except TimeoutError as e:
            return False, 'timeout'

        state, msg = response['state'], response['msg']
        if state:
            return True, 'Register success'
        else:
            return False, msg


    async def request_action(self, client_id, observation, instruction):
        if self.sio is None:
            return False, 'Websocket not connected'
        
        try:
            data = pickle.packb({
                'action': 'get_action',
                'data':{
                    'client_id': client_id,
                    'observation': observation, 
                    'instruction': instruction
                }
            })
            # response = await self.sio.call('message', data, namespace='/', timeout=30)
            await self.sio.send(data)
            response = await self.sio.recv()
            response = json.loads(response)
            print(f'Response: {response}')
        except TimeoutError as e:
            return False, 'timeout'
            
        
        state = response['state']
        if state:
            return True, response['msg']
        else:
            return False, response['msg']


    async def close(self):
        if not self.sio.connected:
            return False, 'Websocket not connected'
        await self.sio.disconnect()
        self.sio = None
        return True, 'Websocket closed'