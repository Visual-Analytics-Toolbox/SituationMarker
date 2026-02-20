import socket
import time
from .GameControlData import GameControlData
import threading

class GameController():
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(('', 3838))
        self.__socket.settimeout(0.5)
        
        self.latest_message = None
        self.lock = threading.Lock()
        self.running = True

    def listen_forever(self):
        self.__socket.setblocking(False)
        while self.running:
            last_packet = None
            # Drain everything currently in the OS buffer
            while True:
                try:
                    data, address = self.__socket.recvfrom(8192)
                    last_packet = data
                except BlockingIOError:
                    break
            
            # parse and return the newest packet
            if last_packet:
                new_msg = GameControlData(last_packet)
                with self.lock: # Protect the write
                    self.latest_message = new_msg
            
            # Give the CPU a tiny break (e.g., 10ms)
            time.sleep(0.01)

    def get_latest(self):
        """The button-press calls this to grab whatever is current."""
        with self.lock:
            return self.latest_message