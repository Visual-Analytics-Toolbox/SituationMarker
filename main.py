
from utils.GameController import TrueGameData,RobotStatusListener,GameData
from utils.logging import get_logger
from vaapi.client import Vaapi
import os
import threading
logging = get_logger()


class SituationMarker():
    def __init__(self,key:str='h'):
        self.key = key
        self.client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
        self.game_data = GameData()
        self.true_game_data = TrueGameData()
        self.robot_status = RobotStatusListener()
        self.is_running = True

        print('press enter to mark a situation\n enter q to stop the programm')
        self.start_threads()
        try:
            while self.is_running:
                import time
                time.sleep(1)
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
        while True:
            a = input("Press Enter to mark, 'q' to quit: ")
            if a.lower() == 'q':
                self.is_running = False
                break
            
            # Grab the freshest data available right now
            true_msg = self.true_game_data.get_latest()
            if true_msg:
                print(true_msg)
                with open('TrueGameData.csv','a') as f:
                    f.write(true_msg+',\n')
            msg = self.game_data.get_latest()
            if msg: 
                print(msg)
                with open('GameData.csv','a') as f:
                    f.write(msg+',\n')
            robot_msg = self.robot_status.get_latest()
            if robot_msg:
                with open('RobotStatus.csv','a') as f:
                    f.writelines(robot_msg)
                    f.write('\n')
            else:
                print("No data received yet...")
                
            
if __name__ == "__main__":
    main = SituationMarker()