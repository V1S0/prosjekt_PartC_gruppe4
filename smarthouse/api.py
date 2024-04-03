import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from smarthouse.persistence import SmartHouseRepository
from smarthouse.domain import SmartHouse
from smarthouse.domain import Device
from pathlib import Path
from typing import Optional


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
        if floor.floorNumber[0] == fid:
            return floor
    return {"error": "Floor not found"}, 404

# Get information about all rooms on a given floor fid
@app.get("/smarthouse/floor/{fid}/room")
def get_rooms_on_floor(fid: int):
    floors = smarthouse.get_floors()
    rooms = smarthouse.get_rooms()
    roomsAtFloor = []
    for room in rooms:
        if room.floor == fid:
            roomsAtFloor.append(room.room_name)
    
    return roomsAtFloor


# Get information about a specific room rid on a given floor fid
@app.get("/smarthouse/floor/{fid}/room/{rid}")
def get_room_info(fid: int, rid: int):

    floors = smarthouse.get_floors()
    rooms = smarthouse.get_rooms()
    roomsAtFloor = []
    for room in rooms:
        if room.floor == fid:
            roomsAtFloor.append(room.room_name)
    return roomsAtFloor[rid]

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
    Device = smarthouse.get_device_by_id(uuid)
    if Device:
        name = Device.model_name
        DeviceType = Device.device_type
        room = Device.room
        roomName = room.room_name
        return f"{name} is a/an {DeviceType} in {roomName}"
    else:
        return {"error": "Device not found"}, 404



@app.get("/smarthouse/sensor/{uuid}/current")
def get_current_sensor_measurement(uuid: str):
    Device = smarthouse.get_device_by_id(uuid)
    name = Device.model_name
    isSensor = Device.is_sensor()
    if isSensor:

        if Device.measurements:

            currentReading = Device.last_measurement()
            value = currentReading.value
            unit = currentReading.unit
            time = currentReading.timestamp
            return (value,unit,time)
        else:
            return f"{name} does not have any measurements"
    else:
        return f"{name} is not a sensor!"
    

@app.post("/smarthouse/sensor/{uuid}/current")
def add_measurement_for_sensor(uuid: str, measurement, unit, time):
    Device = smarthouse.get_device_by_id(uuid)
    name = Device.model_name
    isSensor = Device.is_sensor()

    if isSensor:
        Device.addMeasurement(time, measurement, unit)
        return f"Measurement added successfully to {name}"
    else:
        return f"{name} is not a sensor!"


@app.get("/smarthouse/sensor/{uuid}/values")
def get_sensor_measurements(uuid: str, limit: Optional[int] = None):
    if limit == None:
        limit =0
    
    Device = smarthouse.get_device_by_id(uuid)
    name = Device.model_name
    isSensor = Device.is_sensor()

    if isSensor:
        measuerments = Device.getHistory()
        nvalues = measuerments[-limit:]
        valuesToShow = []
        for reading in nvalues:
            valuesToAdd = (reading.value, reading.unit, reading.timestamp)
            valuesToShow.append(valuesToAdd)
        return valuesToShow
    else:
        return f"{name} is not a sensor!"


@app.delete("/smarthouse/sensor/{uuid}/oldest")
def delete_oldest_sensor_measurement(uuid: str):
    Device = smarthouse.get_device_by_id(uuid)
    name = Device.model_name
    isSensor = Device.is_sensor()
    if isSensor:
        if Device.measurements:
            lastMeasurement = Device.measurements.pop(0)
            time = lastMeasurement.timestamp
            value = lastMeasurement.value
            unit = lastMeasurement.unit

            text = f"the oldest measuerement of {value}{unit} at {time} was removed from {name}"
            return text
        else:
            return f"{name} does not have any measurements"
    else:
        return f"{name} is not a sensor!"

@app.get("/smarthouse/actuator/{uuid}/current")
def get_current_actuator_state(uuid: str):
    Device = smarthouse.get_device_by_id(uuid)
    name = Device.model_name
    isActuator = Device.is_actuator()
    if isActuator:
        state = Device.state
        return f"{name}'s state is {state}"
    else:
        return f"{name} is not an actuator"



    

@app.put("/smarthouse/device/{uuid}")
def update_actuator_state(uuid: str):
    Device = smarthouse.get_device_by_id(uuid)
    isActuator = Device.is_actuator()
    if isActuator:
        name = Device.model_name
        state = Device.state
        Device.state = not state
        return f"{name}'s state was changed from {state} to {Device.state}"
    else:
        return f"{Device.model_name} is not an actuator"
     
    



######dette har jeg laget###########

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)

