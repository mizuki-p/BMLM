import os
import sys

sys.path[0] = os.getcwd()

import subprocess
from EP.Environment.airsim_env import get_env
from EP.View.transfer_viewer import TransferViewer
from EP.manager import BaseClient

# subprocess.Popen(
#     'C:\\Users\\zxcaw\\data\\temp\\agents\\integration\\block\\WindowsNoEditor\\Blocks.exe',
#     shell=True
# )

env, base_env = get_env()
invoker = BaseClient(env)
viewer = TransferViewer(invoker)

viewer.run()
base_env.init()

try:
    while True:
        base_env.do()
        action = env.get_action()
        done = base_env.execute(action)
        if True:
            env.stop_task()
except KeyboardInterrupt:
    pass

viewer.close()
