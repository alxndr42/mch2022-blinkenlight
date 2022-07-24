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
_EFFECT = None


class EffectBase():
    def on_a(self, pressed):
        pass

    def on_b(self, pressed):
        pass

    def __init__(self, neopixel, speed=1):
        self.neopixel = neopixel
        self.speed = speed
        buttons.attach(buttons.BTN_A, self.on_a)
        buttons.attach(buttons.BTN_B, self.on_b)

    def run(self):
        raise Exception('Not implemented.')

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
    """Send a pixel around the outer LEDs in MCH or RGB colors."""
    def run(self):
        self.colors = MCH
        color_idx = 0
        pixel_idx = 0
        while True:
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

    def on_a(self, pressed):
        if pressed:
            print('on_a')
            if self.colors == MCH:
                self.colors = RGB
                print('Switched to RGB')
            else:
                self.colors = MCH
                print('Switched to MCH')


def on_up(pressed):
    if pressed:
        print('on_up')
        if _EFFECT:
            _EFFECT.faster()


def on_down(pressed):
    if pressed:
        print('on_down')
        if _EFFECT:
            _EFFECT.slower()


def on_home(pressed):
    if pressed:
        print('on_home')
        mch22.set_brightness(255)
        mch22.exit_python()


buttons.attach(buttons.BTN_UP, on_up)
buttons.attach(buttons.BTN_DOWN, on_down)
buttons.attach(buttons.BTN_HOME, on_home)
powerPin = Pin(19, Pin.OUT)
powerPin.on()

mch22.set_brightness(0)
_EFFECT = Circle(_NEOPIXEL)
_EFFECT.run()
