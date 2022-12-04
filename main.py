from PIL import Image, ImageDraw, ImageFont
import random
import json
import psutil
import time

with open('./data_cpu.json') as f:
  data = json.load(f)

with open('./data_ram.json') as f:
  data_ram = json.load(f)

#data["data"]
fontSize = 15
font = ImageFont.truetype('./Inter.ttf', fontSize)
input_image = Image.open("transi.png")
pixel_map = input_image.load()
width, height = input_image.size

def get_line(start, end):
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end
 
    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print points2
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
 
    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)
 
    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
 
    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
 
    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1
 
    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1
 
    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx
 
    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points

def normalize(vVal, vMax, eMax):
    return vVal/vMax*eMax

def renderBorder():
    for i in range(width):
        #pixel_map[i, random.randrange(1, height-2)] = (0, 255, 0)
        for j in range(height):
            # print(f"{i}+{j}")
            r, g, b, p = input_image.getpixel((i, j))
            if j == 0 or i == 0 or j == height-1 or i == width-1:
                pixel_map[i, j] = (0, 0, 0)

def clear():
    for i in range(width):
        #pixel_map[i, random.randrange(1, height-2)] = (0, 255, 0)
        for j in range(height):
            # print(f"{i}+{j}")
            r, g, b, p = input_image.getpixel((i, j))
            pixel_map[i, j] = (0, 0, 0, 0)

#Render Data
def renderData(_data, _color=(255,0,0), _textPos=(0,0)):
    points = []
    for i, it in enumerate(_data["data"]):
        dist = width/len(_data["data"])
        for key, value in it.items():
            x = int(dist*(i)+1)
            y = (height-1) - normalize(int(value),100,height-1)
            pixel_map[x,y] = _color
            points.append((int(x),int(y)))
    
    for i, it in enumerate(points):
        if i != len(points)-1:
            linePoints = get_line(points[i], points[i+1])
            for i in linePoints:
                pixel_map[i[0], i[1]] = _color

    d1 = ImageDraw.Draw(input_image)
    d1.text(_textPos, _data["title"], font=font, fill =_color)


def deleteOldData(_data, _seconds):
    for i, it in enumerate(_data["data"]):
        for key, value in it.items():
            if key <= time.time() - _seconds:
                _data["data"].pop(i)
    return _data

def secondsToReadableFormat(_secs):
    if _secs <= 59:
        return f"{_secs} Seconds"
    if _secs >= 60 & _secs <= 59*60:
        return f"{round(_secs / 60)} Minutes"
    if _secs >= 60*59:
        return f"{round(_secs / 60 / 60)} Hours"

while True:
    pixel_map = input_image.load()
    input_image.save("result.png", format="png")
    data["data"].append({time.time():psutil.cpu_percent(5)})
    data_ram["data"].append({time.time():psutil.virtual_memory()[2]})
    #print(data_ram)
    data = deleteOldData(data,60*60*24)
    data_ram = deleteOldData(data_ram,60*60*24)
    clear()

    d1 = ImageDraw.Draw(input_image)
    lastSeconds = list(data_ram["data"][0])
    d1.text((0,0), f"Data of last {secondsToReadableFormat(int(time.time() - lastSeconds[0]))}", font=font, fill = (255,255,255))

    renderBorder()
    renderData(data, (0,0,255), (0,fontSize*1))
    renderData(data_ram, (0,255,0), (0,fontSize*2))
    input_image.save("result.png", format="png")

#input_image.show()g