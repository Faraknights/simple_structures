import json
import os
import sys

from typing import List
    
class BlockData: 
    def __init__(self, X, Y, Z, Type, Colour):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.Type = Type
        self.Colour = Colour
    
    def __hash__(self):
        return hash((self.X, self.Y, self.Z, self.Type, self.Colour))
    
    def __eq__(self, other):
        return (self.X, self.Y, self.Z) == (other.X, other.Y, other.Z)

class WorldState:
    def __init__(self, ChatHistory: List[str], Timestamp: str, blocksInGrid: List[BlockData]):
        self.ChatHistory = ChatHistory
        self.Timestamp = Timestamp
        self.blocksInGrid = blocksInGrid

class Observation:
    def __init__(self, WorldStates: List[WorldState]):
        self.WorldStates = WorldStates

def process_json_file(json_file_path: str, output_folder: str):
    with open(json_file_path, 'r') as file:
        x = json.load(file)

    observation = Observation([WorldState(state['ChatHistory'], state['Timestamp'],
                                          [BlockData(**block) for block in state['BlocksInGrid']])
                              for state in x['WorldStates']])

    BUILDER_NAME = "Builder_B1"
    ARCHITECT_NAME = "Architect_A1"
    textFile = f"dial_with_actions,action_seq\n"
    lastChat = []
    lastBlocksState = set()

    i = 1
    for world in observation.WorldStates:
        if world.ChatHistory != lastChat:
            new_messages = world.ChatHistory[len(lastChat):]
            for message in new_messages:
                text = message.replace("<architect> ", f"{ARCHITECT_NAME} : ").replace("<builder> ", f"{BUILDER_NAME} : ")
                text = message.replace("Mission 0 started", f"<Builder> Mission has started.")
                textFile += f"{text}\n"
                i += 1
            lastChat = world.ChatHistory.copy()

        currentBlocksState = set(world.blocksInGrid)
        if currentBlocksState != lastBlocksState:
            elements_removed = lastBlocksState - currentBlocksState
            elements_added = currentBlocksState - lastBlocksState
            for element in elements_removed:
                textFile += f"pick {element.X} {element.Y} {element.Z}\n"
            i += 1
            for element in elements_added:
                textFile += f"place {element.Colour.lower()} {element.X} {element.Y} {element.Z}\n"
            i += 1
            lastBlocksState = currentBlocksState

    output_file_path = os.path.join(output_folder, os.path.basename(json_file_path).replace('.json', ".txt"))
    with open(output_file_path, "w") as f:
        f.write(textFile)

def main():
    json_folder = "json_games"
    txt_folder = "txt_games"

    if not os.path.exists(txt_folder):
        os.makedirs(txt_folder)

    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    for json_file in json_files:
        json_file_path = os.path.join(json_folder, json_file)
        process_json_file(json_file_path, txt_folder)

if __name__ == "__main__":
    main()
