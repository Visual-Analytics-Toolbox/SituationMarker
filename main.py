
from utils.GameController import GameController
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
        self.controller = GameController()
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
            self.controller.running = False

    def start_threads(self):
        udp_thread = threading.Thread(target=self.controller.listen_forever, daemon=True)
        udp_thread.start()
        
        key_thread = threading.Thread(target=self.key_listener, daemon=True)
        key_thread.start()
                
    def key_listener(self):
        while True:
            a = input("Press Enter to mark, 'q' to quit: ")
            if a.lower() == 'q':
                self.is_running = False
                break
            
            # Grab the freshest data available right now
            msg = self.controller.get_latest()
            if msg:
                print(msg)
            else:
                print("No data received yet...")
                
            
if __name__ == "__main__":
    main = SituationMarker()