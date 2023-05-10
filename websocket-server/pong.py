import copy
import random
import time

import clock
import RPi.GPIO as GPIO


class Pong:
    def __init__(self):
        self.pad_left = Pad(0)
        self.pad_right = Pad(1)
        self.ball = Ball()
        self.currentTick = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(21, GPIO.OUT)

    def get_led_ids(self):
        pixels = []
        pixels.extend(self.pad_left.pixels)
        pixels.extend(self.pad_right.pixels)
        pixels.append(self.ball.pixel)

        led_ids = []
        for pixel in pixels:
            led_ids.append(clock.coordinate_to_led_id(pixel[0], pixel[1]))
        return led_ids

    def tick(self):
        if self.pad_left.bot:
            self.pad_left.move_bot(self.ball)
        if self.pad_right.bot:
            self.pad_right.move_bot(self.ball)

        self.ball.check_pad_collision(self.pad_left)
        self.ball.check_pad_collision(self.pad_right)
        self.ball.move()
        self.currentTick += 1

    def get_sleep_time(self):
        if self.currentTick < 599:
            return 0.14
        elif 600 < self.currentTick < 1119:
            return 0.12
        elif 1200 < self.currentTick < 1799:
            return 0.10
        elif 1800 < self.currentTick < 2399:
            return 0.08
        elif 2400 < self.currentTick < 2999:
            return 0.06
        else:
            return 0.04


class Ball:
    MOTION_LEFT = 0
    MOTION_LEFT_UP = 1
    MOTION_LEFT_DOWN = 2
    MOTION_RIGHT = 3
    MOTION_RIGHT_UP = 4
    MOTION_RIGHT_DOWN = 5

    def __init__(self):
        self.pixel = [5, 5]
        self.motion = self.MOTION_RIGHT

    def respawn(self):
        GPIO.output(21, True)
        self.pixel = [5, 5]
        if random.randint(0, 1) == 0:
            self.motion = self.MOTION_RIGHT
        else:
            self.motion = self.MOTION_LEFT
        time.sleep(0.3)
        GPIO.output(21, False)

    def move(self):
        self.check_goal_collision()
        self.check_border_collision()
        if self.motion == self.MOTION_LEFT:
            self.pixel = [self.pixel[0] - 1, self.pixel[1]]
        if self.motion == self.MOTION_LEFT_DOWN:
            self.pixel = [self.pixel[0] - 1, self.pixel[1] + 1]
        if self.motion == self.MOTION_LEFT_UP:
            self.pixel = [self.pixel[0] - 1, self.pixel[1] - 1]
        if self.motion == self.MOTION_RIGHT:
            self.pixel = [self.pixel[0] + 1, self.pixel[1]]
        if self.motion == self.MOTION_RIGHT_DOWN:
            self.pixel = [self.pixel[0] + 1, self.pixel[1] + 1]
        if self.motion == self.MOTION_RIGHT_UP:
            self.pixel = [self.pixel[0] + 1, self.pixel[1] - 1]

    def check_border_collision(self):
        if self.pixel[1] == 1:
            print("collide")
            if self.motion == self.MOTION_LEFT_UP:
                self.motion = self.MOTION_LEFT_DOWN
            if self.motion == self.MOTION_RIGHT_UP:
                self.motion = self.MOTION_RIGHT_DOWN
        if self.pixel[1] == 10:
            if self.motion == self.MOTION_LEFT_DOWN:
                self.motion = self.MOTION_LEFT_UP
            if self.motion == self.MOTION_RIGHT_DOWN:
                self.motion = self.MOTION_RIGHT_UP

    def check_goal_collision(self):
        if self.pixel[0] == 1:
            self.respawn()
        if self.pixel[0] == 11:
            self.respawn()

    def check_pad_collision(self, pad):
        pad_pixels = copy.deepcopy(pad.get_pixels())
        if pad.position == pad.PAD_LEFT:
            pad_pixels[0][0] += 1
            pad_pixels[1][0] += 1
        if pad.position == pad.PAD_RIGHT:
            pad_pixels[0][0] -= 1
            pad_pixels[1][0] -= 1

        if self.motion == self.MOTION_RIGHT_DOWN:
            pad_pixels.append([pad_pixels[0][0], pad_pixels[0][1] - 1])
        elif self.motion == self.MOTION_LEFT_DOWN:
            pad_pixels.append([pad_pixels[0][0], pad_pixels[0][1] - 1])
        elif self.motion == self.MOTION_RIGHT_UP:
            pad_pixels.append([pad_pixels[1][0], pad_pixels[1][1] + 1])
        elif self.motion == self.MOTION_LEFT_UP:
            pad_pixels.append([pad_pixels[1][0], pad_pixels[1][1] + 1])

        for pixel in pad_pixels:
            if self.pixel == pixel:
                if self.motion == self.MOTION_LEFT or self.motion == self.MOTION_LEFT_UP or self.motion == self.MOTION_LEFT_DOWN:
                    self.motion = random.randint(3, 5)
                else:
                    self.motion = random.randint(0, 2)

class Pad:
    PAD_LEFT = 0
    PAD_RIGHT = 1

    def __init__(self, position):
        self.position = position
        self.bot = True
        if position == 0:
            col = 1
        else:
            col = 11
        self.pixels = [
            [col, 5],
            [col, 6]
        ]

    def move_up(self):
        if self.pixels[0][1] == 1:
            return False
        self.pixels[0][1] -= 1
        self.pixels[1][1] -= 1

    def move_down(self):
        if self.pixels[1][1] == 10:
            return False
        self.pixels[0][1] += 1
        self.pixels[1][1] += 1

    def move_to(self, position):
        self.pixels[0][1] = position
        self.pixels[1][1] = position + 1

    def move_bot(self, ball: Ball):
        h = ball.pixel[1]
        if self.pixels[0][1] > h:
            self.move_up()
        elif self.pixels[0][1] < h:
            self.move_down()

    def get_pixels(self):
        return self.pixels
