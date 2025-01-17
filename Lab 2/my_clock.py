import digitalio
import board
from PIL import Image, ImageDraw
import adafruit_rgb_display.ili9341 as ili9341
from time import strftime, sleep
import adafruit_rgb_display.st7789 as st7789
import time
# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)


# these setup the code for our buttons and the backlight and tell the pi to treat the GPIO pins as digitalIO vs analogIO
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()


if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

# Main loop:
images_dir = 'images/'

def create_image_arr(directory):
    res = []
    for i in range(1, 9):
        res.append(images_dir+directory+str(i)+'.png')
    return res
image = Image.new("RGB", (width, height))

def create_theme():
    res = []
    for i in range(3):
        res.append(create_image_arr('theme'+str(i)+'/'))
    return res

def display_image(file, image):
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    # Draw a black filled box to clear the image.
    # draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    disp.image(image)

    image = Image.open(file)
    backlight = digitalio.DigitalInOut(board.D22)
    backlight.switch_to_output()
    backlight.value = True

    # Scale the image to the smaller screen dimension
    image_ratio = image.width / image.height
    screen_ratio = width / height
    if screen_ratio < image_ratio:
        scaled_width = image.width * height // image.height
        scaled_height = height
    else:
        scaled_width = width
        scaled_height = image.height * width // image.width
    image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

    # Crop and center the image
    x = scaled_width // 2 - width // 2
    y = scaled_height // 2 - height // 2
    image = image.crop((x, y, x + width, y + height))

    # Display image.
    disp.image(image)
# images = create_image_arr()
theme = 0
reset = False
user_time = int(strftime("%H")) // 3
prevTime = 0
themes = create_theme()
print(themes)
change_theme = 0
user_time = int(strftime("%H")) // 3
pre_hit_time = int(strftime("%S"))
while True:
    cur_hit_time = int(strftime("%S"))
    if cur_hit_time < pre_hit_time:
        cur_hit_time += 60
    if cur_hit_time - pre_hit_time > 5:
        user_time = int(strftime("%H")) // 3
    if not buttonA.value and not buttonB.value:
        theme += 1 
        pre_hit_time = int(strftime("%S"))
    theme %= 3
    
    # user_time = hour if reset else user_time
    
   

    if not buttonB.value and buttonA.value:  # just button A pressed
        user_time += 1
        pre_hit_time = int(strftime("%S"))
    if not buttonA.value and buttonB.value:  # just button B pressed
        user_time -= 1
        pre_hit_time = int(strftime("%S"))

    user_time %= 8
    if user_time != prevTime:
        prevTime = user_time
        print(theme, user_time)
        display_image(themes[theme][user_time], image)
    print(user_time)
    # im = 'images/5.png'
    # display_image(im)
    
    # print(strftime("%H"))
    # time.sleep(0.1)