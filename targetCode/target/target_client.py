import network
import socket
from time import sleep
import machine
from machine import Pin, PWM, ADC
from creds import ssid, password, controller_IP, target_name
import json
import struct
import os
from microdot import Microdot, Request, Response
import urequests
import asyncio
import utime

servo = PWM(Pin(16))
servo.freq(50)

piezo_in = ADC(Pin(26))

def interval_mapping(x, in_min, in_max, out_min, out_max):
 return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def servo_write(pin,angle):
 pulse_width=interval_mapping(angle, 0, 180, 0.5,2.5)
 duty=int(interval_mapping(pulse_width, 0, 20, 0,65535))
 pin.duty_u16(duty)

def activate(time_duration):
# Activate servo to stand up. If piezo exceeds threshold, lay back down and return true
# If time is exceeded, lay back down and return false
    servo_write(servo, 90)
    utime.sleep(.5)
    start_time = utime.ticks_ms()
    # while utime.ticks_diff(utime.ticks_ms(), start_time) < :
    while utime.ticks_diff(utime.ticks_ms(), start_time) < time_duration:
        pot_value = piezo_in.read_u16()
        if pot_value > 10000:
            servo_write(servo, 0)
            return True

    return False

# ws = websocket.WebSocket
PORT = 8081

app = Microdot()

@app.get('/')
def index(request):
    return 'Hello, from Pico'

@app.post('/target')
def handle_target(request):
   data = json.loads(request.data)
   time_duration = data.get('time_duration', None)
   if time_duration is not None:
       # Call your activate function here with time_duration
       was_hit = activate(time_duration)
       result = "Hit" if was_hit else "Miss"
       jsonMessage = {"sender": target_name, "message": result}
       return Response(json.dumps(jsonMessage), 200, 'json')
    #    return Response(json.dumps(jsonMessage), 200, 'json')
    #    return Response(str(result), mimetype='application/json')
   else:
       return Response('Invalid request', 400)


pico_led = Pin("LED", Pin.OUT)

def ping_controller():
    ipAddr = f'http://{controller_IP}:{PORT}'
    response = urequests.get(ipAddr)
    # response = urequests.post(f'http://{controller_IP}:8081', json=message)
    if response.status_code == 200:
        print("Successfully connected to controller and sent message.")
        print(response.text)
    else:
        print("Failed to connect to controller. Status code:", response.status_code)
    response.close()

def connect_to_controller():
    message = {"sender": "rpi", "message": "Hello from RPi"}
    ipAddr = "http://192.168.11.99:8081/"
    response = urequests.get(ipAddr)
    # response = urequests.post(f'http://{controller_IP}:8081', json=message)
    if response.status_code == 200:
        print("Successfully connected to controller and sent message.")
        print(response.text)
    else:
        print("Failed to connect to controller. Status code:", response.status_code)
    response.close()

def send_to_controller(message):
    ipAddr = f'http://{controller_IP}:{PORT}/message'
    jsonMessage = {"sender": target_name, "message": message}
    response = urequests.post(ipAddr, json=jsonMessage)
    if response.status_code == 200:
        print("Successfully connected to controller and sent message.")
        print(response.text)
    else:
        print("Failed to connect to controller. Status code:", response.status_code)
        print(response.text)
    response.close()
    
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)    
    # print(wlan.ifconfig())
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    pico_led.on()
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    #connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(address)
    connection.listen(1)
    # print(connection)
    return connection

def webpage(temperature, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <p>LED is {state}</p>
            <p>Temperature is {temperature}</p>
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            pico_led.on()
            state = "ON"
        elif request =='/lightoff?':
            pico_led.off()
            state = "OFF"
        html = webpage(temperature, state)
        client.send(html)
        client.close()

try:
    ip = connect()
    # send_to_controller("Hello from RPi")
    print("Starting Microdot server...")
    app.run(port=80, host=ip)
    # connection = open_socket(ip)
    # serve(connection)
    pico_led.off()
except KeyboardInterrupt:
    pico_led.off()
    machine.reset()
