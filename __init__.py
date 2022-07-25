import random
import time

import buttons
from machine import Pin
import mch22
from neopixel import NeoPixel


OFF = (0, 0, 0)

_DATAPIN = Pin(5, Pin.OUT)
_NEOPIXEL = NeoPixel(_DATAPIN, 5)
_EFFECTS = None
_ACTIVE = 0


class ColorCycle():
    def __init__(self):
        self.color = [255, 0, 0]
        self.color_idx = 1
        self.fade_in = True

    def next(self, step=1):
        value = self.color[self.color_idx]
        if self.fade_in:
            if value < 255:
                self.color[self.color_idx] = min(255, value + step)
            else:
                self.fade_in = False
                self.color_idx = (self.color_idx - 1) % 3
        else:
            if value > 0:
                self.color[self.color_idx] = max(0, value - step)
            else:
                self.fade_in = True
                self.color_idx = (self.color_idx + 2) % 3
        return self.color


class EffectBase():
    speed = 1

    def __init__(self, neopixel):
        self.neopixel = neopixel
        self.active = False

    def run(self):
        raise Exception('Not implemented.')

    def stop(self):
        self.active = False

    def faster(self):
        if EffectBase.speed < 2:
            EffectBase.speed += 0.1
            print(f'Speed: {EffectBase.speed}')

    def slower(self):
        if EffectBase.speed > 0.1:
            EffectBase.speed -= 0.1
            print(f'Speed: {EffectBase.speed}')

    def update(self, colors):
        for index, color in enumerate(colors):
            self.neopixel[index] = color
        self.neopixel.write()


class Circle(EffectBase):
    """Send a pixel around the outer LEDs."""
    def __init__(self, neopixel):
        super().__init__(neopixel)

    def run(self):
        color_cycle = ColorCycle()
        pixel_idx = 0
        self.active = True
        while self.active:
            color = color_cycle.next(15)
            pixels = [OFF for i in range(self.neopixel.n)]
            pixels[1] = color
            if pixel_idx == 1:
                pixel_idx += 1
            pixels[pixel_idx] = color
            pixel_idx = (pixel_idx + 1) % self.neopixel.n
            self.update(pixels)
            time.sleep(0.25 / EffectBase.speed)


class Palette(EffectBase):
    """Cycle through the color palette on all LEDs."""
    def run(self):
        color_cycle = ColorCycle()
        self.active = True
        while self.active:
            color = color_cycle.next()
            colors = [color for i in range(self.neopixel.n)]
            self.update(colors)
            time.sleep(0.01 / EffectBase.speed)


class Random(EffectBase):
    """Light a random pixel."""
    def __init__(self, neopixel):
        super().__init__(neopixel)

    def run(self):
        color_cycle = ColorCycle()
        pixel = 0
        next_pixel = 0
        self.active = True
        while self.active:
            colors = [OFF for i in range(self.neopixel.n)]
            colors[pixel] = color_cycle.next(15)
            self.update(colors)
            while next_pixel == pixel:
                next_pixel = random.randint(0, self.neopixel.n - 1)
            pixel = next_pixel
            time.sleep(0.2 / EffectBase.speed)


class Runner(EffectBase):
    """Run a pixel back and forth."""
    def __init__(self, neopixel, pixels):
        super().__init__(neopixel)
        self.pixels = pixels

    def run(self):
        color_cycle = ColorCycle()
        pixel_idx = 0
        forward = True
        self.active = True
        while self.active:
            colors = [OFF for i in range(self.neopixel.n)]
            colors[self.pixels[pixel_idx]] = color_cycle.next(15)
            self.update(colors)
            if forward:
                pixel_idx += 1
                if pixel_idx < len(self.pixels):
                    sleep = 0.25 / EffectBase.speed
                else:
                    pixel_idx -= 2
                    forward = False
                    sleep = 0.45 / EffectBase.speed
            else:
                pixel_idx -= 1
                if pixel_idx >= 0:
                    sleep = 0.25 / EffectBase.speed
                else:
                    pixel_idx = 1
                    forward = True
                    sleep = 0.45 / EffectBase.speed
            time.sleep(sleep)


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
    Circle(_NEOPIXEL),
    Runner(_NEOPIXEL, [4, 1, 2]),
    Random(_NEOPIXEL),
]
while True:
    print(f'Active: {_ACTIVE}')
    _EFFECTS[_ACTIVE].run()
