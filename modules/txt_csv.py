import csv
import json

class WaypointsConverter:
   def __init__(self,config_file) -> None:
      self.config_file = config_file
      self.load_config()

   def load_config(self):
      try:
        with open(self.config_file ,'r') as f:
             # Load JSON data
             self.config_data = json.load(f)
             self.waypoints_files = [self.config_data["waypoints_file_waypoint"] ,self.config_data["fence_file_waypoint"] ,self.config_data["payload_file_waypoint"] ]
             self.csv_files = [self.config_data["waypoints_file_csv"],self.config_data["fence_file_csv"],self.config_data["payload_file_csv"]]
      except FileNotFoundError:
        print(f"JSON file '{self.config_file}' not found.")
      except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
      except KeyError as e:
        print(f"KeyError: Missing key {e}")
      except Exception as e:
        print(f"An error occurred: {e}")  
   def convert(self):
      for n in range(len(self.waypoints_files)) :
        try:
          with open(self.waypoints_files[n],'r') as txtfile,open(self.csv_files[n], 'w', newline='', encoding='utf-8') as csvfile:
                  self.txt_data = txtfile.readlines()
                  self.csv_data = csv.writer(csvfile)
                  self.csv_data.writerow(["lat", "long","alt"])
                  for i,line in enumerate(self.txt_data):
                      if i <= 1:
                          continue
                      words = line.strip().split()
                      if len(words) >= 10:  # Ensure there are enough words in the line
                          lat = words[8]
                          long = words[9]
                          alt= words[10]
                          self.csv_data.writerow([lat, long,alt])
                      else:
                          print(f"Invalid format in line: {line}. Skipping.")

        except FileNotFoundError:
              print(f"The file '{self.waypoints_file_txt}' was not found.")
        except IOError:
              print(f"An error occurred while trying to read/write the files.")    