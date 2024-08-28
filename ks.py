import re as _re
from collections import defaultdict
from json import dump
import os as _os
import time

def parse_vessel_data(data):
    def parse_block(lines):
        block_dict = defaultdict(list)
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if '=' in line:
                key, value = map(str.strip, line.split('=', 1))
                block_dict[key] = value
            elif '{' in line:
                key = line.split('{')[0].strip()
                sub_block_lines = []
                brace_count = 1
                i += 1
                while brace_count > 0:
                    line = lines[i].strip()
                    if '{' in line:
                        brace_count += 1
                    if '}' in line:
                        brace_count -= 1
                    if brace_count > 0:
                        sub_block_lines.append(line)
                    i += 1
                sub_block_dict = parse_block(sub_block_lines)
                block_dict[key].append(sub_block_dict)
                continue
            i += 1
        return dict(block_dict)

    lines = data.strip().split('\n')
    vessel_dict = parse_block(lines[1:])
    return vessel_dict


class vessel:
    def __init__(self, raw_text: str):
        self.raw = raw_text
        while self.raw.count("{") < self.raw.count("}"):
            self.raw = self.raw[:-1]
        while self.raw.count("{") > self.raw.count("}"):
            self.raw += "}"
        
             
        self.data = parse_vessel_data(raw_text)[""][0]
        


class save:
    def __init__(self, save_folder: str):
        if not save_folder.endswith("/"):
            save_folder+="/"
        self.folder = save_folder
        self.location = save_folder+"persistent.sfs"
        self.data = open(self.location).read()
        
        self.vessels = []
        
        self.vessel_start_index = self.data.index("VESSEL")
        self.vessel_end_index = self.data.index("LoaderInfo")
        
        _raw = self.data[self.vessel_start_index:self.vessel_end_index]
        
        parts = _raw.split("VESSEL\n\t\t{")
    
        vessels = []

        for part in parts[1:]:
            vessels.append("VESSEL\n\t\t{" + part)

        self.vessels = []

        for vesseldata in vessels:
            self.vessels.append(vessel(vesseldata))
    
    def get_vessels(self):
        self.vessels = []
        
        self.vessel_start_index = self.data.index("VESSEL")
        self.vessel_end_index = self.data.index("LoaderInfo")
        
        _raw = self.data[self.vessel_start_index:self.vessel_end_index]
        
        parts = _raw.split("VESSEL\n\t\t{")
    
        vessels = []

        for part in parts[1:]:
            vessels.append("VESSEL\n\t\t{" + part)

        self.vessels = []

        for vesseldata in vessels:
            self.vessels.append(vessel(vesseldata))
        return self.vessels
    
    def listvessels(self):
        for vessel in self.vessels:
            print(vessel.data["name"])
            
    def addvessel(self, vessel_to_add: vessel):
        self.vessels.append(vessel_to_add)
        
    def remove_vessel(self, vessel_pid_to_delete: str):
        for vessel_data in self.vessels:
            if vessel_data.data["pid"] == vessel_pid_to_delete:
                self.vessels.remove(vessel_data)
    
    def remove_vessel_by_name(self, vessel_name: str):
        for vessel_data in self.vessels:
            if vessel_data.data["name"] == vessel_name:
                self.vessels.remove(vessel_data)
    
    def save(self, save_name: str = "persistent"):
        raw_vessel_data = ""
        for vessel_data in self.vessels:
            raw = vessel_data.raw
            # i = 0
            # while raw[(-40+i):].count("}") > 3:
            #     raw = raw[:-1]
            #     i+=1
            
                
            raw_vessel_data += raw
        
        self.raw_vessel_data = raw_vessel_data
        self.data = open(self.location, "r").read()
        self.vessel_start_index = self.data.index("VESSEL")
        self.vessel_end_index = self.data.index("LoaderInfo")
        pre = self.data[:self.vessel_start_index]
        aft = self.data[self.vessel_end_index:]
        self.data = pre+raw_vessel_data+"}"+aft
        open(self.folder+save_name+".sfs", "w").write(self.data)
    
    def get_vessel_by_name(self, name:str):
        for v in self.vessels:
            if v.data["name"] == name:
                return v
        return None
            

class server:
    def __init__(self, folder: str):
        if not folder.endswith("/"):
            folder+="/"
        
        self.name = folder[:-1].split("/")[-1]
        self.folder = folder
        
    def get_vessels(self):
        vessel_folder = self.folder+"active_vessels/"
        vessels = _os.listdir(vessel_folder)
        server_vessels = []
        for vsl in vessels:
            server_vessels.append(vessel(open(vessel_folder + vsl, "r").read()))
            
        return server_vessels
    
    def upload_vessel(self, vessel: vessel):
        vessel_folder = self.folder+"active_vessels/"
        vessels = _os.listdir(vessel_folder)
        if vessel.data["name"]+".vsl" in vessels:
            file = open(self.folder+"active_vessels/"+vessel.data["name"]+".vsl", "w")
        else:
            file = open(self.folder+"active_vessels/"+vessel.data["name"]+".vsl", "x")
        
        file.write(vessel.raw)
        _os.makedirs(self.folder+"../upload_data/"+self.name+"/", exist_ok=True)
        try:
            file = open(self.folder+"../../client/upload_data/"+self.name+"/"+vessel.data["name"]+".json", "x")
        except FileExistsError:
            file = open(self.folder+"../../client/upload_data/"+self.name+"/"+vessel.data["name"]+".json", "w")
        except FileNotFoundError:
            file = open(self.folder+"../../client/upload_data/"+self.name+"/"+vessel.data["name"]+".json", "x")
        except:
            pass
        else:
            file = open(self.folder+"../../client/upload_data/"+self.name+"/"+vessel.data["name"]+".json", "w")
        
        data = {"last_local_update": time.time()+10}
        
        dump(data, file)
    
    def get_vessel_by_name(self, name: str):
        for v in self.get_vessels():
            if v.data["name"] == name:
                return v
        
        return None