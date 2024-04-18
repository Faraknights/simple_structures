import json
import os
import sys

from typing import List
import pandas as pd
    
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

    lastChat = []
    lastBlocksState = set()
    
    data_rows = []
    data = {'dial_with_actions': '', 'action_seq': ''}
    for i, world in enumerate(observation.WorldStates):
        if world.ChatHistory != lastChat:
            if i != 0:
                data_rows.append(data)
                data = {'dial_with_actions': '', 'action_seq': ''}
                new_messages = world.ChatHistory[len(lastChat):]
                for message in new_messages:
                    data["dial_with_actions"] += f"{message}\n"
            lastChat = world.ChatHistory.copy()

        currentBlocksState = set(world.blocksInGrid)
        if currentBlocksState != lastBlocksState:
            elements_removed = lastBlocksState - currentBlocksState
            elements_added = currentBlocksState - lastBlocksState
            for element in elements_removed:
                data["action_seq"] += f"pick {element.X} {element.Y} {element.Z}\n"
            for element in elements_added:
                data["action_seq"] += f"place {element.Colour.lower()} {element.X} {element.Y} {element.Z}\n"
            lastBlocksState = currentBlocksState

    if data['dial_with_actions'] or data['action_seq']:
        data_rows.append(data)

    return pd.DataFrame(data_rows)     

def main():
    json_folder = "json_games"
    txt_folder = "txt_games"

    if not os.path.exists(txt_folder):
        os.makedirs(txt_folder)

    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    data = {
        'dial_with_actions': [],
        'action_seq': []
    }
    df = pd.DataFrame(data)
    for json_file in json_files:
        
        json_file_path = os.path.join(json_folder, json_file)
        new_df = process_json_file(json_file_path, txt_folder)
        new_df.drop(2, inplace=True)
        new_df.drop(0, inplace=True)
        df = pd.concat([df, new_df], ignore_index=True)
    
    output_file_path = "games.csv"
    with open(output_file_path, "w") as f:
        df.to_csv(f, index=False, lineterminator='\n')
        

if __name__ == "__main__":
    main()
