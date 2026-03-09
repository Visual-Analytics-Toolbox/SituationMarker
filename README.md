# Situtation Marker
This little tool can mark situations that are happening live in a RoboCup SPL game. If it has a connection to our Visual Analytics Backend it will publish the situations live. 
The tool only works if a game controller is connected.

## Setup GameController
Setup the game controller from https://github.com/RoboCup-SPL/GameController3/tree/master

## Configuration

TODO: introduce single and double mode here


## Usage
start with
```bash
uv run main.py -i <your-local-ip>
```
This script listens to gamecontroller messages and writes the true game data, the data the robot recieved and all robot status messages to a .jsonl file

to test logging of robot messages run
```bash
uv run robot.py -p <player-num> -t <team-id> -i <other-local-ip>
```

default ip that sockets are bound to is '' but  two diffrent IP Adresses are required to send robot messages with the emulator and monitor the game on the same device

when running this in WSL I ran GameController on eth0 and created a temporary second IP like this:
```bash
sudo ip addr add 192.168.1.50/24 dev eth0
```

## Old
start with
```bash
uv run main.py
```
This script listens to gamecontroller messages and whenever it recieves an enter press it creates a new situation for the selected game

in case vaapi couldn't be imported try

```bash
uv add ../../sdk
```