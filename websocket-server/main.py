import asyncio
import datetime
import math
import json
import random
import subprocess
import sys
import time

import pytz
import websockets
import clock
import pong

CONNECTIONS = set()
MODE = "clock"
BRIGHTNESS = 0
COLOR = [0, 0, 0, 255]
PONG = None


async def register(websocket):
    CONNECTIONS.add(websocket)
    await websocket.send(get_new_settings())
    try:
        async for message in websocket:
            event = json.loads(message)
            mode = event["mode"]
            global PONG
            global MODE
            global BRIGHTNESS
            global COLOR

            if mode == "pong":
                if PONG is None:
                    PONG = pong.Pong()
                MODE = mode
                websockets.broadcast(CONNECTIONS, get_new_settings())
            elif mode == "movePaddle":
                if PONG is not None:
                    event["position"] = int(event["position"])
                    if event["pad"] == 0:
                        PONG.pad_left.move_to(event["position"])
                        PONG.pad_left.bot = False
                    else:
                        PONG.pad_right.move_to(event["position"])
                        PONG.pad_right.bot = False
                    response = json.dumps({
                        "mode": MODE,
                        "color": COLOR,
                        "brightness": BRIGHTNESS,
                        "data": {
                            "leds": PONG.get_led_ids(),
                        }
                    })
                    websockets.broadcast(CONNECTIONS, response)

            elif mode != "movePaddle":
                MODE = mode
                BRIGHTNESS = event["brightness"]
                color = [event["color"][0], event["color"][1], event["color"][2], event["color"][3]]
                COLOR = color
                if mode != "pong":
                    print("fuck")
                    PONG = None
                websockets.broadcast(CONNECTIONS, get_new_settings())

        await websocket.wait_closed()
    finally:
        CONNECTIONS.remove(websocket)


def get_new_settings():
    response = json.dumps({
        "mode": "setSettings",
        "color": COLOR,
        "brightness": BRIGHTNESS,
        "currentMode": MODE
    })
    return response


async def tick_clock():
    while True:
        sleep_time = 0.5
        if MODE == "clock":
            now = datetime.datetime.now(pytz.timezone('Europe/Zurich'))
            hours = now.strftime("%I")
            minutes = now.minute

            partminutes = minutes % 5
            fullminutes = math.floor(minutes / 5) * 5
            fullminutes = f'{fullminutes:02d}'

            timestring = hours + ":" + fullminutes

            if partminutes == 1:
                minutepoints = ["oneminute"]
            elif partminutes == 2:
                minutepoints = ["oneminute", "twominutes"]
            elif partminutes == 3:
                minutepoints = ["oneminute", "twominutes", "threeminutes"]
            elif partminutes == 4:
                minutepoints = ["oneminute", "twominutes", "threeminutes", "fourminutes"]
            else:
                minutepoints = []

            words = []
            words.extend(clock.TIMES[timestring])
            words.extend(["es", "ist"])

            words.extend(minutepoints)

            leds = []

            for word_key in words:
                word_leds = clock.WORDS[word_key]
                leds.extend(word_leds)

            message = json.dumps({
                "mode": MODE,
                "color": COLOR,
                "brightness": BRIGHTNESS,
                "data": {
                    "leds": leds,
                }
            })
        elif MODE == "lighting":
            message = json.dumps({
                "mode": MODE,
                "color": COLOR,
                "brightness": BRIGHTNESS,
                "data": {

                }
            })
        elif MODE == "pong":
            global PONG
            PONG.tick()
            sleep_time = PONG.get_sleep_time()
            message = json.dumps({
                "mode": MODE,
                "color": COLOR,
                "brightness": BRIGHTNESS,
                "data": {
                    "leds": PONG.get_led_ids(),
                }
            })
        elif MODE == "disco":
            message = json.dumps({
                "mode": MODE,
                "color": COLOR,
                "brightness": BRIGHTNESS,
                "data": {
                    "leds": [],
                }
            })

        websockets.broadcast(CONNECTIONS, message)
        await asyncio.sleep(sleep_time)


async def main():
    async with websockets.serve(register, "localhost", 5678):
        await tick_clock()


if __name__ == "__main__":
    subprocess.Popen([sys.executable, './clock-controller/main.py'])
    asyncio.run(main())
