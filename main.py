
from utils.GameController import TrueGameData,RobotStatusListener,GameData
from utils.logging import get_logger
from vaapi.client import Vaapi
import os
import threading
import json
import uuid
import argparse
logging = get_logger()


class SituationMarker():
    def __init__(self,key:str='h',ip:str=''):
        self.key = key
        self.client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
        self.game_data = GameData()
        self.true_game_data = TrueGameData(ip)
        self.robot_status = RobotStatusListener(ip)
        self.is_running = True

        print('press enter to mark a situation\n enter q to stop the programm')
        self.start_threads()
        try:
            while self.is_running:
                import time
                time.sleep(1)
                if self.game_data.game_controller_address and not self.true_game_data.monitor:
                    self.true_game_data.target_ip = self.game_data.game_controller_address
                    self.true_game_data.register_as_monitor()
                if self.game_data.game_controller_address and not self.robot_status.monitor:
                    self.robot_status.target_ip = self.game_data.game_controller_address
                    self.robot_status.register_as_monitor()

        except KeyboardInterrupt:
            pass
        finally:
            print("Exiting application.")
            # Optional: tell the controller thread to stop too
            self.game_data.running = False
            self.true_game_data.running = False
            self.robot_status.running = False

    def start_threads(self):
        game_data_thread = threading.Thread(target=self.game_data.listen_forever, daemon=True)
        game_data_thread.start()

        true_game_data_thread = threading.Thread(target=self.true_game_data.listen_forever, daemon=True)
        true_game_data_thread.start()

        robot_status_thread = threading.Thread(target=self.robot_status.listen_forever, daemon=True)
        robot_status_thread.start()
        
        key_thread = threading.Thread(target=self.key_listener, daemon=True)
        key_thread.start()
                
    def key_listener(self):
        with open('Situations.jsonl', 'a') as f_situation:
            while True:
                cycle_uuid = str(uuid.uuid4())
                
                a = input("Press Enter to mark, 'q' to quit: ")
                if a.lower() == 'q':
                    self.is_running = False
                    break
                
                record = {"uuid":cycle_uuid}

                true_msg = self.true_game_data.get_latest()
                if true_msg:
                    record["TrueGameData"]=true_msg.json()
                                    
                msg = self.game_data.get_latest()
                if msg: 
                    record["GameData"] = msg.json()
                    
                robot_messages = self.robot_status.get_latest()
                if robot_messages:
                    record["RobotStatus"] = [robot_msg.json() for robot_msg in robot_messages]

                if not robot_messages and not true_msg and not msg:
                    print("No data received yet...")
                else:
                    f_situation.write(json.dumps(record)+ '\n')
                    f_situation.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Situation Marker.")
    
    parser.add_argument("-i", "--ip", type=str, default="", help="IP address to bind to (default: '')")
    
    args = parser.parse_args()

    #bind socket to diffrent IP than the robot emulator runs on
    main = SituationMarker(ip=args.ip)