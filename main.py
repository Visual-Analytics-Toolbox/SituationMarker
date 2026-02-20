
from utils.GameController import GameController
from utils.logging import get_logger
from vaapi.client import Vaapi
import os
from queue import Queue
import threading
from iterfzf import iterfzf
logging = get_logger()


class SituationMarker():
    def __init__(self,key:str='h'):
        self.key = key
        self.client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
        self.queue = Queue()
        self.controller = GameController()
        
        self.game = None
        
        #self.menu()
        print('press enter to mark a situation\n enter q to stop the programm')
        self.start_threads()
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting application.")

    def start_threads(self):
        game_thread = threading.Thread(target=self.game_listener,args=(self.queue,),daemon=True)
        game_thread.start()
        key_thread = threading.Thread(target=self.key_listener, args=(self.queue,), daemon=True)
        key_thread.start()
        
    def menu(self):
        try:
            games = self.client.games.list()
            if games:
                game_map = {f"{game.start_time}: {game.team1} vs {game.team2} {game.half}": game for game in games}
                selected_str = iterfzf(game_map.keys())
                if selected_str:
                    selected_game = game_map[selected_str]
                    self.game = selected_game.id
            else:
                print('couldn''nt find any games')    
        except Exception as e:
            logging.error(e)
       
                
    def key_listener(self, q):
        while True:
            # TODO: find better way for input
            a = input()
            if a != 'q':
                q.put('msg')
            else:
                quit()
            
    def game_listener(self,q):
        while True:
            msg = q.get()
            if msg == 'msg':
                message = self.controller.run()
                if message:
                    print(message)
                    #self.client.situation.create(game=self.game,message=message.json())
            q.task_done()
                
            
if __name__ == "__main__":
    main = SituationMarker()