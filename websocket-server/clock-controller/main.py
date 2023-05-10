import asyncio
import json
import math
import random
import time
import websockets

import ADS1x15
from rpi_ws281x import Color, PixelStrip, ws


def set_all(color):
    for i in range(0, 114):
        strip.setPixelColor(i, color)
    strip.show()


def set_all_without_show(color):
    for i in range(0, 114):
        strip.setPixelColor(i, color)


initial_voltage = 0
last_brightness = 0
passed_ticks = 0
last_change = 0


def get_automatic_brightness():
    global last_brightness
    global passed_ticks
    print(ADS.getValue())
    voltage = ADS.toVoltage(ADS.getValue())
    print(voltage)

    max_brightness_voltage = 0.7
    min_brightness_voltage = 0.56

    if voltage >= max_brightness_voltage:
        brightness = 100
    else:
        difference = max_brightness_voltage - min_brightness_voltage  # 0.3
        next_brightness = (100 / difference) * (voltage - min_brightness_voltage)
        if next_brightness < 50:
            min_diff = 9
        else:
            min_diff = 15
        if abs(last_brightness - next_brightness) >= min_diff:
            brightness = next_brightness
        else:
            brightness = last_brightness
    last_brightness = brightness
    return brightness


async def hello():
    uri = "ws://localhost:5678"
    global last_change
    async with websockets.connect(uri) as websocket:
        while True:
            event = await websocket.recv()
            event = json.loads(event)
            mode = event["mode"]
            if mode == "setSettings":
                continue
            color = event["color"]
            brightness = event["brightness"]
            if brightness == 0:
                current = int(time.time())
                if current > last_change + 2:
                    brightness = get_automatic_brightness()
                    last_change = current
                    print(brightness)
                else:
                    brightness = last_brightness

            data = event["data"]
            col = Color(math.ceil(color[0] / 100 * brightness), math.ceil(color[1] / 100 * brightness),
                        math.ceil(color[2] / 100 * brightness), math.ceil(color[3] / 100 * brightness))

            if mode == "clock" or mode == "pong":
                # print(data)
                leds = data["leds"]
                set_all_without_show(Color(0, 0, 0, 0))
                for led in leds:
                    strip.setPixelColor(led, col)
                strip.show()
            if mode == "lighting":
                set_all(col)
            if mode == "disco":
                set_all_without_show(Color(0, 0, 0, 0))
                for led in range(0, 114):
                    strip.setPixelColor(led, Color(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)))
                strip.show()


if __name__ == "__main__":
    ADS = ADS1x15.ADS1115(1, 0x48)
    ADS.setGain(1)
    ADS.setDataRate(ADS.DR_ADS111X_8)
    ADS.setMode(ADS.MODE_CONTINUOUS)
    ADS.requestADC(0)
    strip = PixelStrip(114, 18, 800000, 10, False, 255, 0, ws.SK6812_STRIP_GRBW)
    strip.begin()
    set_all(Color(0, 0, 0, 0))
    asyncio.run(hello())
