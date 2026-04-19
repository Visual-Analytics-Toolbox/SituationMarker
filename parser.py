from utils.GameControlData import GameControlReturnData
import base64

msg = "UkdydAQBBAEAAAAAAAAAAAAAAAAAAIC/AAAAAAAAAAA="

decoded_msg = base64.b64decode(msg)

b = GameControlReturnData(bytes(decoded_msg))
print(b.json())