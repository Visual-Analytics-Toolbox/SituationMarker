import socket
import logging
from .GameControlData import GameControlData


class GameController():
    """
    The GameController class is used to receive the infos of a game.
    If new data was received, it gets parsed and published on the blackboard.
    """

    def __init__(self):
        """
        Constructor.
        Init class variables and establish the udp socket connection to the GameController.
        """
        self.__source = None
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.__socket.bind(('', 3838))
        self.__socket.settimeout(1)  # in sec
        
        
    def run(self):
        try:
            data, address = self.__socket.recvfrom(8192)
            
            if len(data) > 0:
                if self.__source is None or address[0] == self.__source:
                    message = GameControlData(data)
                    logging.info(message.secsRemaining)
                    return message
        except Exception as e:
            logging.error(e)
            return None