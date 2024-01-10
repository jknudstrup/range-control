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

VERBOSE = False
PORT = 8081

app = Microdot()

def say(text):
    if VERBOSE:
        print(text)


def interval_mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def servo_write(pin, angle):
    pulse_width = interval_mapping(angle, 0, 180, 0.5, 2.5)
    duty = int(interval_mapping(pulse_width, 0, 20, 0, 65535))
    pin.duty_u16(duty)


def activate(time_duration):
    # Activate servo to stand up. If piezo exceeds threshold, lay back down and return true
    # If time is exceeded, lay back down and return false
    servo_write(servo, 90)
    utime.sleep(.5)
    start_time = utime.ticks_ms()
    was_hit = False
    while utime.ticks_diff(utime.ticks_ms(), start_time) < time_duration:
        pot_value = piezo_in.read_u16()
        if pot_value > 10000:
            say(pot_value)
            servo_write(servo, 0)
            was_hit = True

    say(f'Target {target_name} was hit: {was_hit}')
    servo_write(servo, 0)
    send_to_controller(str(was_hit))





@app.get('/')
def index(request):
    return 'Hello, from Pico'


@app.post('/target')
def handle_target(request):
    data = request.json
    time_duration = data['time_duration']
    if time_duration is not None:
        say(f'Setting up target to stand for {time_duration} milliseconds.')
        activate(time_duration)
        return Response(f'Activating target {target_name}', 200)
    else:
        return Response('Invalid request', 400)


pico_led = Pin("LED", Pin.OUT)


def ping_controller():
    ipAddr = f'http://{controller_IP}:{PORT}'
    response = urequests.get(ipAddr)
    if response.status_code == 200:
        say("Successfully connected to controller and sent message.")
        say(response.text)
    else:
        say("Failed to connect to controller. Status code:" + str(response.status_code))
    response.close()


def connect_to_controller():
    message = {"sender": "rpi", "message": "Hello from RPi"}
    ipAddr = "http://192.168.11.99:8081/"
    response = urequests.get(ipAddr)
    if response.status_code == 200:
        say("Successfully connected to controller and sent message.")
        say(response.text)
    else:
        say("Failed to connect to controller. Status code:" + str(response.status_code))
    response.close()


def send_to_controller(message):
    ipAddr = f'http://{controller_IP}:{PORT}/message'
    jsonMessage = {"sender": target_name, "message": message}
    response = urequests.post(ipAddr, json=jsonMessage)
    if response.status_code == 200:
        say("Successfully connected to controller and sent message.")
        say(response.text)
    else:
        say("Failed to connect to controller. Status code:" + str(response.status_code))
        say(response.text)
    response.close()


def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        say('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    say(f'Connected on {ip}')
    pico_led.on()
    return ip


def open_socket(ip):
    # Open a socket
    # Postponed until further notice
    address = (ip, 80)
    connection = socket.socket()
    # connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(address)
    connection.listen(1)
    return connection

def connect_and_serve():
    ip = connect()
    app.run(port=80, host=ip)

try:
    connect_and_serve()
    pico_led.off()
except KeyboardInterrupt:
    pico_led.off()
    machine.reset()
