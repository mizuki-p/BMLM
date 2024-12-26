from enum import Enum, auto


class ViewMode(Enum):
    Transfer = auto()
    SelfHost = auto()
    
    
class ViewDataFlow(Enum):
    Active = auto()
    Passive = auto()