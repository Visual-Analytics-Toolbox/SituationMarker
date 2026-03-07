import socket
import struct
import time
from utils.GameControlData import GameControlData,GameControlReturnData
import threading

class Robot():
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(('', 3838))
        self.__socket.settimeout(0.5)
        self.target_ip = ""
        self.request_port = 3939
        self.latest_message = None
        self.lock = threading.Lock()
        self.running = True
        #self.register_as_monitor()

    def send_status(self):
        packet = GameControlReturnData(playerNum=4,teamNum=4,fallen=0).pack()
        
        print(f"Sending monitor request to {self.target_ip}:{self.request_port}...")
        self.__socket.sendto(packet, (self.target_ip[0], self.request_port))

    def listen_forever(self):
        self.__socket.setblocking(False)
        while self.running:
            last_packet = None
            last_adress = None
            # Drain everything currently in the OS buffer
            while True:
                try:
                    data, address = self.__socket.recvfrom(8192)
                    if data.startswith(b'RGme'):
                        last_packet = data
                        last_adress = address
                        
                except BlockingIOError:
                    break
            
            # parse and return the newest packet
            if last_packet:
                new_msg = GameControlData(last_packet)
                with self.lock: # Protect the write
                    self.latest_message = new_msg
                    self.target_ip = last_adress
            
            # Give the CPU a tiny break (e.g., 10ms)
            time.sleep(0.01)

    def get_latest(self):
        """The button-press calls this to grab whatever is current."""
        with self.lock:
            return self.latest_message,self.latest_adress

# listen to broadcast udp on 3838

# send udp unicast on 3939

class RobotEmulator():

    def __init__(self):      
        self.robot = Robot()
        self.is_running = True
        self.start_threads()
        try:
            while self.is_running:
                import time
                time.sleep(1)
                self.robot.send_status()
        except KeyboardInterrupt:
            pass
        finally:
            print("Exiting application.")
            self.robot.running = False

    def start_threads(self):
        udp_thread = threading.Thread(target=self.robot.listen_forever, daemon=True)
        udp_thread.start()

bla = RobotEmulator()