from typing import Callable, Any, TypeAlias
from queue import Queue
from ..types import ViewMode, ViewDataFlow

Observation : TypeAlias = Any
Action : TypeAlias = Any
Image : TypeAlias = Any


class BaseEnv:
    def __init__(
        self,
        env_name: str,
        scene_name: str,
        
        nop_code: Any,
        observation_captor : Callable[[], Observation],
        action_executor : Callable[[Action], None],
        check_init: Callable[[], bool],
        reset_env: Callable[[], None],
        
        view_mode: ViewMode,
        # if view_mode == ViewMode.SelfHost
        get_view_url: Callable[[], str] = None,
        
        # if view_mode == ViewMode.Transfer
        view_data_flow: ViewDataFlow = None,
        
        # if view_data_flow == ViewDataFlow.Active
        video_pusher: Callable[[Callable[[], bool]], Image] = None, 
        
        # if view_data_flow == ViewDataFlow.Passive
        frame_rate: int = None,
        frame_captor: Callable[[], Image] = None,
        
        task_done_callback: Callable[[], None] = None
    ):
        self.env_name = env_name
        self.scene_name = scene_name
        
        self.nop_code = nop_code
        
        self.get_observation = observation_captor
        self.step = action_executor
        self.check_init = check_init
        self.reset_env = reset_env
        
        self.view_mode = view_mode
        if view_mode == ViewMode.SelfHost:
            assert get_view_url is not None, 'get_view_url must be provided if view_mode is SelfHost'
            self.get_view_url = get_view_url
        elif view_mode == ViewMode.Transfer:
            assert view_data_flow is not None, 'view_data_flow must be provided if view_mode is Transfer'
            self.view_data_flow = view_data_flow
            self.video_pusher = video_pusher
            if view_data_flow == ViewDataFlow.Passive:
                assert frame_rate is not None, 'frame_rate must be provided if view_data_flow is Passive'
                assert frame_captor is not None, 'frame_captor must be provided if view_data_flow is Passive'
                self.frame_rate = frame_rate
                self.frame_captor = frame_captor
        
        self.task_done_callback = task_done_callback
        
        self.action_queue = Queue()
        self.event_queue = Queue()

        
    def get_view_url(self) -> str:
        if self.view_mode == ViewMode.SelfHost:
            return self.get_view_url()
        else:
            raise NotImplementedError('get_view_url is not available in Transfer mode')
    
    def get_action(self):
        if self.action_queue.empty():
            return self.nop_code
        else:
            return self.action_queue.get()
        
    def add_action(self, action: Action):
        self.action_queue.put(action)
        
    def stop_task(self):
        if self.task_done_callback is not None:
            self.task_done_callback()
    
    def do_sth(self):
        if not self.event_queue.empty():
            event = self.event_queue.get()
            event()
    
    def put_event(self, event: Callable[[], None]):
        self.event_queue.put(event)