from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
import json

app = FastAPI()

# Store the dummy data and active WebSocket clients
dummy_data: List[List[float]] = []
active_clients: List[WebSocket] = []

# Template directory for HTML responses
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def get(request: Request):
    """
    Homepage showing real-time sensor data visualization
    """
    return templates.TemplateResponse("index.html", {"request": request})



@app.get("/data")
async def get_data():
    """
    Endpoint to view the dummy data as an HTML table.
    """
    # Create an HTML table from dummy_data
    table_html = "<table border='1'><tr><th>Sensor_1</th><th>Sensor_2</th><th>Sensor_3</th><th>Sensor_4</th><th>Sensor_5</th><th>Sensor_6</th><th>Sensor_7</th><th>sensor_8</th><th>Sensor_9</th><th>Sensor_10</th><th>Sensor_11</th><th>Sensor_12</th><th>Sensor_13</th><th>Sensor_14</th><th>Sensor_15</th><th>Sensor_16</th></tr>"
    
    for row in dummy_data:
        table_html += "<tr>" + "".join([f"<td>{col}</td>" for col in row]) + "</tr>"
    
    table_html += "</table>"
    
    return HTMLResponse(content=table_html, status_code=200)



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_clients.append(websocket)
    try:
        while True:
            # Receive data from client (ESP32)
            data = await websocket.receive_text()
            print(f"Received data: {data}")
            
            # Parse and store the data
            try:
                columns = list(map(float, data.split(',')))
                if len(columns) == 16:
                    dummy_data.append(columns)
                    # Broadcast the new data to all connected clients
                    for client in active_clients:
                        await client.send_text(f"new_data:{','.join(map(str, columns))}")
                else:
                    print("Invalid data format, expecting 16 columns.")
            except ValueError as e:
                print(f"Error parsing data: {e}")

    except WebSocketDisconnect:
        active_clients.remove(websocket)
        print("Client disconnected")