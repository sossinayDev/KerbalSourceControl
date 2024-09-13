import ks as ksp
import os
from time import sleep, time
from keyboard import is_pressed
from json import load, loads, dump, dumps
def clear():
    for e in range(50):
        print()

try:
    try:
        server_data = load(open("servers.json", "r"))
    except:
        server_data = {}
        open("servers.json", "x").write("{}")
    serverlist = list(server_data.keys())
    serverlist.append("+ Add server")


    selecting = True
    select_i = 0
    while selecting:
        clear()
        print("Your servers: ")
        i = 0
        for server in serverlist:
            if i == select_i:
                print(">> " + server)
            else:
                print(server)
            i+=1
        
        
        
        while not (is_pressed("down") or is_pressed("up") or is_pressed("enter")):
            sleep(0.1)
        
        if is_pressed("down"):
            while is_pressed("down"):
                sleep(0.1)
            select_i += 1
            if select_i >= len(serverlist):
                select_i = len(serverlist)-1
        
        if is_pressed("up"):
            while is_pressed("up"):
                sleep(0.1)
            select_i -= 1
            if select_i < 0:
                select_i = 0
        
        if is_pressed("enter"):
            while is_pressed("enter"):
                sleep(0.1)
            selecting = False

    input()

    if serverlist[select_i] != "+ Add server":
        server_folder = server_data[serverlist[select_i]]
        server_name = serverlist[select_i]
    else:
        server_folder = input("Enter path:\n")
        server_name = server_folder.replace("\ ".strip(), "/").split("/")[-1]
        server_data[server_name] = server_folder
        try:
            dump(server_data, open("servers.json", "w"))
        except:
            dump(server_data, open("servers.json", "x"))

    if not server_folder.endswith("/"):
        server_folder+="/"
    print(server_folder)

    server = ksp.server(server_folder)
    while not os.path.exists(f"C:/Program Files (x86)/Steam/steamapps/common/Kerbal Space Program/saves/{server_name}/persistent.sfs"):
        print(f"Create the world ingame. Name the world '{server_name}'")
        input("Press enter to continue")
    persistent = ksp.save(f"C:/Program Files (x86)/Steam/steamapps/common/Kerbal Space Program/saves/{server_name}/")


    while 1:
        
        todo_upload = []
        todo_download = []
        server_vessels = []
        v_names = []
        
        
        
        for s_v in server.get_vessels():
            if not s_v.data["type"] == "SpaceObject":
                server_vessels.append(s_v.data["name"])

        for v in persistent.get_vessels():
            if not v.data["type"] == "SpaceObject":
                v_names.append(v.data["name"])

        for vessel in v_names:
            if not vessel in server_vessels:
                todo_upload.append(vessel)
                print("New local vessel created")
            
        for s_vessel in server_vessels:
            if not s_vessel in v_names:
                todo_download.append(s_vessel)
                print("New vessel available")
            try:
                if os.path.getmtime(server_folder+"active_vessels/"+s_vessel+".vsl") > load(open("upload_data/"+server_name+"/"+s_vessel+".json", "r"))["last_local_update"]:
                    if not s_vessel in todo_download:
                        todo_download.append(s_vessel)
                        print("Newer version available")
            except Exception as e:
                print(str(e))
                if not s_vessel in todo_download:
                    todo_download.append(s_vessel)



        sleep(1)

        
        if len(todo_download) + len(todo_upload) == 0:
            print("No changes are pending.")

            input()
        else:
            print("Confirm changes:\n")
            for upload in todo_upload:
                print(f"Vessel {upload} needs to be uploaded.")
                ans = input("Upload? (y/n)")
                if ans == "y":
                    server.upload_vessel(persistent.get_vessel_by_name(upload))
                    print("Vessel uploaded.")
                else:
                    print("Cancelled.")
                    
            for download in todo_download:
                print(f"Vessel {download} needs to be downloaded.")
                ans = input("Download? (y/n)")
                if ans == "y":
                    try:
                        persistent.remove_vessel_by_name(download)
                    except:
                        pass
                    sleep(0.5)
                    persistent.addvessel(server.get_vessel_by_name(download))
                    data = {"last_local_update": time()+10}
                    os.makedirs("./upload_data/"+server_name+"/", exist_ok=True)
                    try:
                        dump(data, open("./upload_data/"+server_name+"/"+download+".json", "w"))
                    except:
                        print("Error writing vessel data. Is the vessel name compatible? (No * | % & etc?)")
                    print("Vessel downloaded.")
                else:
                    print("Cancelled.")
                    
            print("Saving changes...")
            persistent.save("LATEST VERSION ONLINE")
        clear()
        print("Press enter to scan again")
        input()
except Exception as e:
    print("An error has ocurred:\n")
    print(str(e))
    try:
        file = open("KSC.log", "+a")
    except FileNotFoundError:
        file = open("KSC.log", "x")
    for line in str(e).splitlines:
        file.write(line)
    file.write("\n=======================================\n")