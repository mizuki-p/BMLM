import airsim
from .base_env import BaseEnv
from ..types import ViewDataFlow, ViewMode
from .airsim_utils.car_wrapper import CarWrapper
from .airsim_utils.drone_wrapper import DroneWrapper

from typing import Callable
import cv2
import re
import numpy as np
import queue

class DiscardingQueue(queue.Queue):
    def __init__(self, maxsize):
        super().__init__(maxsize)

    def put(self, item, block=True, timeout=None):
        with self.not_full:
            # 如果队列已满，则丢弃最早的元素
            if self.full():
                self.get_nowait()  # 丢弃队头元素，不阻塞
            super().put(item, block, timeout)


class AirSimEnv:
    def __init__(self):
        self.car_wrapper = CarWrapper()
        self.drone_wrapper = DroneWrapper()
        
        self.car_inited = False 
        self.drone_inited = False
        
        self.start_fetch_images = False
        self.images = queue.Queue()
        
        self.query_obs = False
        self.obs = None
    
    def init(self):
        self.car_wrapper.init()
        self.car_inited = True
        self.drone_wrapper.init()
        self.drone_inited = True
    
    
    def check_init(self):
        return self.car_inited and self.drone_inited
    
    
    def execute(self, action):
        if action is None:
            return
        print('execute action:', action)
        def extract_python_code(content):
            # code_block_regex = re.compile(r"```(.*?)```", re.DOTALL)
            # code_blocks = code_block_regex.findall(content)
            # if code_blocks:
            #     full_code = "\n".join(code_blocks)

            #     if full_code.startswith("python"):
            #         full_code = full_code[7:]

            #     return full_code
            # else:
            #     return None
            if content is None:
                return 'print("💩")'
            print(f'[content] : {content}')
            code = content[0]
            return code
        
        done = True
        exec(extract_python_code(action), {
            'car': self.car_wrapper,
            'drone': self.drone_wrapper,
        })
        return done


    def push_image_stream(self, alive: Callable[[], bool]):
        self.start_fetch_images = True
        while alive():
            if self.images.empty():
                continue
            data = self.images.get(block=True, timeout=None)
            yield data
        self.start_fetch_images = False


    def observe(self):
        self.query_obs = True
        while self.obs is None:
            continue
        drone_image, car_image = self.obs
        self.obs = None

        image = np.concatenate((drone_image, car_image), axis=1)
        _, buffer = cv2.imencode('.png', image)
        frame_bytes = buffer.tobytes()
        return frame_bytes


    def do(self):
        if not hasattr(self, 'do_counter'):
            self.do_counter = 0
        if self.start_fetch_images:
            drone_image = self.drone_wrapper.query_image()
            car_image = self.car_wrapper.query_image()
            image = np.concatenate((drone_image, car_image), axis=0)
            _, buffer = cv2.imencode('.jpg', image)
            frame_bytes = buffer.tobytes()
            data = b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            self.images.put(data)
            print(f'put image {self.do_counter}')
            self.do_counter += 1
        if self.query_obs:
            print(f'query obs')
            drone_image = self.drone_wrapper.query_image()
            car_image = self.car_wrapper.query_image()
            print(f'put obs')
            self.obs = (drone_image, car_image)
            self.query_obs = False
        

airsim_env = AirSimEnv()
def get_env():
    return BaseEnv(
        env_name='Airsim',
        scene_name='Simple Block',
        nop_code=None,
        
        observation_captor=airsim_env.observe,
        action_executor=airsim_env.execute,
        
        check_init=airsim_env.check_init,
        reset_env= lambda : None,
        
        view_mode=ViewMode.Transfer,
        view_data_flow=ViewDataFlow.Active,
        video_pusher=airsim_env.push_image_stream
    ), airsim_env
    
