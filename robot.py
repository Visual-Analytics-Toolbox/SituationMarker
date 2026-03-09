import socket
import struct
import time
from utils.GameControlData import GameControlData,GameControlReturnData
import threading
import argparse

class Robot():
    def __init__(self,player,team,local_ip):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(('', 3838))
        self.__socket.settimeout(0.5)

        self.__send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__send_socket.bind((local_ip, 0)) 

        self.player = player
        self.team = team
        self.target_ip = ""
        self.request_port = 3939
        self.latest_message = None
        self.lock = threading.Lock()
        self.running = True

    def send_status(self):
        if not self.target_ip:
            return
        packet = GameControlReturnData(playerNum=self.player,teamNum=self.team,fallen=0).pack()
        
        print(f"Sending monitor request to {self.target_ip}:{self.request_port}...")
        self.__send_socket.sendto(packet, (self.target_ip[0], self.request_port))

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

class RobotEmulator():

    def __init__(self,player,team,ip):      
        self.robot = Robot(player,team,ip)
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Robot Emulator.")
    
    parser.add_argument("-p", "--player", type=int, default=3, help="Player ID (default: 3)")
    parser.add_argument("-t", "--team", type=int, default=4, help="Team ID (default: 4)")
    parser.add_argument("-i", "--ip", type=str, default="", help="IP address to bind to (default:'')")
    
    args = parser.parse_args()

    # bind RobotEmulator to diffrent address than SituationMarker
    emulator = RobotEmulator(args.player, args.team, args.ip)