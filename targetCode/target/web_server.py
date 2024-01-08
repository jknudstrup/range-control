import network
import socket
from time import sleep
# from picozero import pico_temp_sensor, pico_led
import machine
from machine import Pin
from creds import ssid, password, controller_IP
import json
import struct
import os


pico_led = Pin("LED", Pin.OUT)

def send_frame(sock, opcode, data):
   print("Sending frame...")


   fin = 0x80
   mask = 0x00
   length = len(data)
   if length <= 125:
       header = struct.pack('!BB', fin | opcode, mask | length)
   elif length > 125 and length < 65536:
       header = struct.pack('!BBH', fin | opcode, mask | 126, length)
   else:
       header = struct.pack('!BBQ', fin | opcode, mask | 127, length)

   masking_key = os.urandom(4)
   data = bytes([b ^ k for b, k in zip(data, masking_key * (len(data) // 4) + masking_key[:len(data) % 4])])
   sock.send(header + data)

def connect_to_controller():
    print("Connecting to controller...")
    sock = socket.socket()
    sock.connect((controller_IP, 8081))
    handshake = f'GET / HTTP/1.1\r\nHost: {controller_IP}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n\r\n'
    sock.send(handshake)
    response = sock.recv(1024)
    print(response)
    print("Handshake complete")
    sleep(1)
    message = "Your message here"
    # sock.send(message.encode())
    send_frame(sock, 0x01, message.encode())
    # print("Sending encoded message...")
    # msgJson = json.dumps({"sender": "rpi", "message": "Hello from RPi"})
    # msg = msgJson.encode(json.dumps([json.dumps({"msg": msgJson})]))
    # sock.send(json.dumps([json.dumps({"msg": msgJson})]))
    # print("Sending some guys thing from Stackoverflow...")
    # sock.send(json.dumps([json.dumps({'msg': 'connect', 'version': '1', 'support': ['1', 'pre2', 'pre1']})]))
    # sock.send(msg)

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
        # temperature = pico_temp_sensor.temp
        html = webpage(temperature, state)
        client.send(html)
        client.close()

try:
    # machine.reset()
    ip = connect()
    connect_to_controller()
    pico_led.off()
    # ip = controller_IP
    # connection = open_socket(ip)
    # print(connection)
    # serve(connection)
except KeyboardInterrupt:
    pico_led.off()
    machine.reset()