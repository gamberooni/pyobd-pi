from sense_hat import SenseHat
from time import sleep

sense = SenseHat()

R = [255, 0, 0]
G = [0, 255, 0]
B = [0, 0, 255]
Bk = [0, 0, 0]
O = [100, 100, 100]  # background
W = [255, 255, 255]

pepe = [
O, O, O, O, O, O, O, O,
O, G, G, O, O, G, G, O,
G, G, G, G, G, G, G, O,
G, G, W, Bk, G, W, Bk, O,
G, G, G, G, G, G, G, O,
B, G, R, R, R, R, R, O,
B, G, G, G, G, G, O, O,
B, B, B, B, B, B, O, O
]

def init_led():
    sense.clear()
    sense.low_light = True
    sense.set_pixels(pepe)
    sense.flip_v()

def pepe_led():
    sense.flip_h()
    sleep(0.25) 

init_led()
while 1:
    pepe_led()

#sense.clear()
#sense.set_pixel(0, 7, 0,0,255)