# Situtation Marker
This little tool can mark situations that are happening live in a RoboCup SPL game. If it has a connection to our Visual Analytics Backend it will publish the situations live. 
The tool only works if a game controller is connected.

## Setup GameController
Setup the game controller from ... TODO: insert link here

## Configuration
TODO: introduce single and double mode here


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