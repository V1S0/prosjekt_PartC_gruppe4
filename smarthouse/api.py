import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from smarthouse.persistence import SmartHouseRepository
from smarthouse.domain import SmartHouse
from smarthouse.domain import Device
from pathlib import Path

##husk husk##
#source .venv/bin/activate
#uvicorn smarthouse.api:app --reload


def setup_database():
    project_dir = Path(__file__).parent.parent
    db_file = project_dir / "data" / "db.sql" # you have to adjust this if you have changed the file name of the database
    print(db_file.absolute())
    return SmartHouseRepository(str(db_file.absolute()))

app = FastAPI()

repo = setup_database()

smarthouse = repo.load_smarthouse_deep()

# http://localhost:8000/welcome/index.html
app.mount("/static", StaticFiles(directory="www"), name="static")


# http://localhost:8000/ -> welcome page
@app.get("/")
def root():
    return RedirectResponse("/static/index.html")


# Health Check / Hello World
@app.get("/hello")
def hello(name: str = "world"):
    return {"hello": name}


# Starting point ...

@app.get("/smarthouse")
def get_smarthouse_info() -> dict[str, int | float]:
    """
    This endpoint returns an object that provides information
    about the general structure of the smarthouse.
    """
    return {
        "no_rooms": len(smarthouse.get_rooms()),
        "no_floors": len(smarthouse.get_floors()),
        "registered_devices": len(smarthouse.get_devices()),
        "area": smarthouse.get_area()
    }

# TODO: implement the remaining HTTP endpoints as requested in
# https://github.com/selabhvl/ing301-projectpartC-startcode?tab=readme-ov-file#oppgavebeskrivelse
# here ...


########dette har jeg laget #########

# Get information on all floors
@app.get("/smarthouse/floor")
def get_smarthouse_floor():
    return smarthouse.get_floors()

# Get information about a floor given by fid
@app.get("/smarthouse/floor/{fid}")
def get_floor_info(fid: int):
    floors = smarthouse.get_floors()
    for floor in floors:
        print(floor.floorNumber[0])
        if floor.floorNumber[0] == fid:
            return floor
    return {"error": "Floor not found"}, 404

# Get information about all rooms on a given floor fid
@app.get("/smarthouse/floor/{fid}/room")
def get_rooms_on_floor(fid: int):
    floors = smarthouse.get_floors()
    rooms = smarthouse.get_rooms()
    #print(rooms)
    roomsAtFloor = []
    for room in rooms:
        #print(room.floor)
        if room.floor == fid:
            #print(room.room_name)
            roomsAtFloor.append(room.room_name)
    
    #print(roomsAtFloor)
    return roomsAtFloor


# Get information about a specific room rid on a given floor fid
@app.get("/smarthouse/floor/{fid}/room/{rid}")
def get_room_info(fid: int, rid: int):

    floors = smarthouse.get_floors()
    rooms = smarthouse.get_rooms()
    #print(rooms)
    roomsAtFloor = []
    for room in rooms:
        #print(room.floor)
        if room.floor == fid:
            #print(room.room_name)
            roomsAtFloor.append(room.room_name)
    return roomsAtFloor[rid]


    """
    floors = smarthouse.get_floors()
    for floor in floors:
        if floor.floorNumber == fid:
            rooms = floor.get_rooms()
            for room in rooms:
                if room.id == rid:
                    return room
    return {"error": "Room not found"}, 404
    """




# Get information on all devices
@app.get("/smarthouse/device")
def get_smarthouse_device():
    alldevices = []
    devices = smarthouse.get_devices()
    for device in devices:
        navn = device.model_name
        alldevices.append(navn)
    return alldevices

# Get information for a given device identified by uuid
@app.get("/smarthouse/device/{uuid}")
def get_device_info(uuid: str):
    devices = smarthouse.get_devices()
    for device in devices:
        if device.id == uuid:
            return device.model_name
    return {"error": "Device not found"}, 404


@app.get("/smarthouse/sensor/{uuid}/current")
def get_current_sensor_measurement(uuid: str):
    devices = smarthouse.get_devices()
    for device in devices:
        if device.id == uuid:
            device.addMeasurement(19,"%",101010)
            currentReading = device.last_measurement()
            value = currentReading.value
            unit = currentReading.unit
            time = currentReading.timestamp

            return (value,unit,time)
    return {"error": "no measurement found"}, 404


@app.post("/smarthouse/sensor/{uuid}/current")
def add_measurement_for_sensor(uuid: str, measurement, unit, time):
    sensor = smarthouse.get_device_by_id(uuid)
   
    sensor.addMeasurement(time, measurement, unit)
    
    return {"message": "Measurement added successfully"}


######dette har jeg laget###########

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)

