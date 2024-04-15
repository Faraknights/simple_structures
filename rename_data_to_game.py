import os

folder_path = "json_games"
files = os.listdir(folder_path)

for filename in files:
    if filename.startswith("data (") and filename.endswith(").json"):
        number = filename.split("(")[1].split(")")[0]
        new_filename = f"game_{number}.json"
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))
        print(f"Renamed {filename} to {new_filename}")
