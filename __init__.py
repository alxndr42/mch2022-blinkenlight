import time

import buttons
from machine import Pin
import mch22
from neopixel import NeoPixel


MCH = [(0x49, 0x1d, 0x88), (0xfa, 0x44, 0x8c), (0x43, 0xb5, 0xa0)]
RGB = [(0xff, 0, 0), (0, 0xff, 0), (0, 0, 0xff)]
OFF = (0, 0, 0)

_DATAPIN = Pin(5, Pin.OUT)
_NEOPIXEL = NeoPixel(_DATAPIN, 5)
_EFFECTS = None
_ACTIVE = 0


class EffectBase():
    def __init__(self, neopixel):
        self.neopixel = neopixel
        self.speed = 1
        self.active = False

    def run(self):
        raise Exception('Not implemented.')

    def stop(self):
        self.active = False

    def faster(self):
        if self.speed < 2:
            self.speed += 0.1
            print(f'Speed: {self.speed}')

    def slower(self):
        if self.speed > 0.1:
            self.speed -= 0.1
            print(f'Speed: {self.speed}')

    def update(self, colors):
        for index, color in enumerate(colors):
            self.neopixel[index] = color
        self.neopixel.write()


class Circle(EffectBase):
    """Send a pixel around the outer LEDs."""
    def __init__(self, neopixel, colors):
        super().__init__(neopixel)
        self.colors = colors

    def run(self):
        self.active = True
        color_idx = 0
        pixel_idx = 0
        while self.active:
            on = self.colors[color_idx]
            pixels = [OFF for i in range(self.neopixel.n)]
            pixels[1] = on
            if pixel_idx == 1:
                pixel_idx += 1
            pixels[pixel_idx] = on
            pixel_idx = (pixel_idx + 1) % self.neopixel.n
            self.update(pixels)
            time.sleep(0.25 / self.speed)
            if pixel_idx == 0:
                color_idx = (color_idx + 1) % len(self.colors)


class Palette(EffectBase):
    """Cycle through the color palette on all LEDs."""
    def run(self):
        self.active = True
        color = [255, 0, 0]
        color_idx = 1
        fade_in = True
        while self.active:
            colors = [color for i in range(self.neopixel.n)]
            self.update(colors)
            if fade_in:
                if color[color_idx] < 255:
                    color[color_idx] += 1
                else:
                    fade_in = False
                    color_idx = (color_idx - 1) % 3
            else:
                if color[color_idx] > 0:
                    color[color_idx] -= 1
                else:
                    fade_in = True
                    color_idx = (color_idx + 2) % 3
            time.sleep(0.01 / self.speed)


def on_up(pressed):
    if pressed:
        print('on_up')
        _EFFECTS[_ACTIVE].faster()


def on_down(pressed):
    if pressed:
        print('on_down')
        _EFFECTS[_ACTIVE].slower()


def on_a(pressed):
    if pressed:
        print('on_a')
        global _ACTIVE
        _EFFECTS[_ACTIVE].stop()
        _ACTIVE = (_ACTIVE + 1) % len(_EFFECTS)


def on_b(pressed):
    if pressed:
        print('on_b')
        global _ACTIVE
        _EFFECTS[_ACTIVE].stop()
        _ACTIVE = (_ACTIVE - 1) % len(_EFFECTS)


def on_home(pressed):
    if pressed:
        print('on_home')
        mch22.set_brightness(255)
        mch22.exit_python()


buttons.attach(buttons.BTN_UP, on_up)
buttons.attach(buttons.BTN_DOWN, on_down)
buttons.attach(buttons.BTN_A, on_a)
buttons.attach(buttons.BTN_B, on_b)
buttons.attach(buttons.BTN_HOME, on_home)
powerPin = Pin(19, Pin.OUT)
powerPin.on()
mch22.set_brightness(0)

_EFFECTS = [
    Palette(_NEOPIXEL),
    Circle(_NEOPIXEL, MCH),
    Circle(_NEOPIXEL, RGB),
]
while True:
    print(f'Active: {_ACTIVE}')
    _EFFECTS[_ACTIVE].run()
