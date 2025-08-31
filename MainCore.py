import threading

import MainFuncs as call

active = True


def mainLoop():
    print('camera started')
    camera_thread = threading.Thread(target=call.raw_camera_start)
    camera_thread.start()

    call.begin()

    call.listening_loop()
    # End of Program
