import socket
import struct
import time
from .GameControlData import GameControlData,GameControlReturnData
import threading

class TrueGameData():
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(('', 3838))
        self.__socket.settimeout(0.5)
        
        self.request_port = 3636
        self.target_ip = "127.0.0.1"

        self.latest_message = None
        self.lock = threading.Lock()
        self.running = True
        self.register_as_monitor()
    
    def register_as_monitor(self):
        """Sends the 5-byte 'RGTr' + \x00 packet to the controller."""
        header = b'RGTr'
        version = struct.pack('B', 0) # 1 byte unsigned char (0)
        packet = header + version
        
        print(f"Sending monitor request to {self.target_ip}:{self.request_port}...")
        self.__socket.sendto(packet, (self.target_ip, self.request_port))

    def listen_forever(self):
        self.__socket.setblocking(False)
        while self.running:
            last_packet = None
            # Drain everything currently in the OS buffer
            while True:
                try:
                    data, address = self.__socket.recvfrom(8192)
                    if data.startswith(b'RGTD'):
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

class RobotStatusListener():
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(('', 3940))
        self.__socket.settimeout(0.5)
        
        self.request_port = 3636
        self.target_ip = "127.0.0.1"
        self.latest_messages = {}
        self.lock = threading.Lock()
        self.running = True
        self.register_as_monitor()

    def register_as_monitor(self):
        """Sends the 5-byte 'RGTr' + \x00 packet to the controller."""
        header = b'RGTr'
        version = struct.pack('B', 0) # 1 byte unsigned char (0)
        packet = header + version
        
        print(f"Sending monitor request to {self.target_ip}:{self.request_port}...")
        self.__socket.sendto(packet, (self.target_ip, self.request_port))

    def listen_forever(self):
        self.__socket.setblocking(False)
        while self.running:
            last_packets = []
            # Drain everything currently in the OS buffer
            while True:
                try:
                    data, address = self.__socket.recvfrom(8192)
                    header_index = data.find(b'RGrt')
                    if header_index != -1:
                          last_packets.append(data[header_index:])
                    
                except BlockingIOError:
                    break
            
            # parse and return the newest packet
            if last_packets:
                new_msgs_this_cycle = {}
                
                for packet in last_packets:
                    msg = GameControlReturnData(packet)
                    key = (msg.teamNum, msg.playerNum)
                    new_msgs_this_cycle[key] = msg
                
                with self.lock:
                    for key, msg in new_msgs_this_cycle.items():
                        self.latest_messages[key] = msg
            
            # Give the CPU a tiny break (e.g., 10ms)
            time.sleep(0.01)

    def get_latest(self):
        """The button-press calls this to grab whatever is current."""
        with self.lock:
            return list(self.latest_messages.values())

class GameData():
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
                    if data.startswith(b'RGme'):
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