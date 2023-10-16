"""
Class that handles drawing the image of a generated map
"""

from PIL import Image, ImageDraw

from constants import *

class Canvas:
    def __init__(self, width, height, bg):
        self.width = width
        self.height = height
        self.bg = bg
        self.img = Image.new('RGBA', (self.width, self.height), self.bg)
        self.draw = ImageDraw.Draw(self.img)

    def drawLine(self, points, fill=None, width=0):
        self.draw.line(points, fill=fill, width=width)

    def drawRect(self, points, fill=None, outline=None, width=0):
        self.draw.rectangle(points, fill=fill, outline=outline, width=width)

    def drawHex(self, origin, size, fill=HEX_BG, outline=HEX_OUTLINE, width=HEX_THICKNESS):
        center_x, center_y = origin

        def calculatePoint(i):
            degrees = 60 * i
            radians = math.pi / 180 * degrees
            point = (center_x + size * math.cos(radians),
                     center_y + size * math.sin(radians))

            return point

        coords = []
        for i in range(6):
            coords.append(calculatePoint(i))
        self.draw.polygon(coords, fill=fill, outline=outline, width=width)

    def drawText(self, origin, string, anchor='mm', font=FONT_SMALL, fill=None, direction='rtl', bg=True):
        center_x, center_y = origin

        if bg:
            width, height = font.getsize(string)
            self.draw.rectangle((center_x - width // 2 - FONT_PADDING,
                                 center_y - height // 2 - FONT_PADDING,
                                 center_x + width // 2 + FONT_PADDING,
                                 center_y + height // 2 + FONT_PADDING),
                                fill=HEX_BG)

        self.draw.text(origin, string, anchor=anchor, font=font, fill=fill, direction=direction)

    def drawCircle(self, origin, size, fill=None, outline=None, width=1):
        center_x, center_y = origin
        bounds = [ (center_x - size, center_y - size), (center_x + size, center_y + size) ]
        self.draw.ellipse(bounds, fill=fill, outline=outline, width=width)

    def drawEllipse(self, origin, size, fill=None, outline=None):
        center_x, center_y = origin
        bounds = [ (center_x - size, center_y - size // 4), (center_x + size, center_y + size // 4) ]
        self.draw.ellipse(bounds, fill=fill, outline=outline)

    def drawPolestar(self, origin, size, fill=None, outline=None):
        center_x, center_y = origin

        def calculatePoint(i):
            point_size = size
            if i % 2:
                point_size = size // 3

            degrees = 45 * i
            radians = math.pi / 180 * degrees
            point = (center_x + point_size * math.cos(radians),
                     center_y + point_size * math.sin(radians))

            return point

        coords = []
        for i in range(8):
            coords.append(calculatePoint(i))
        self.draw.polygon(coords, fill=fill, outline=outline)

    def drawStarburst(self, origin, size, fill=None, outline=None):
        center_x, center_y = origin

        def calculatePoint(i):
            point_size = size
            if i % 2:
                point_size = int(size * 2/5)

            degrees = 30 * i
            radians = math.pi / 180 * degrees
            point = (center_x + point_size * math.cos(radians),
                     center_y + point_size * math.sin(radians))

            return point

        coords = []
        for i in range(12):
            coords.append(calculatePoint(i))
        self.draw.polygon(coords, fill=fill, outline=outline)

    def drawStar(self, origin, size, fill=None, outline=None):
        center_x, center_y = origin

        def calculatePoint(i):
            point_size = size
            if i % 2:
                point_size = int(size * 2/5)

            degrees = 36 * i - 18
            radians = math.pi / 180 * degrees
            point = (center_x + point_size * math.cos(radians),
                     center_y + point_size * math.sin(radians))

            return point

        coords = []
        for i in range(10):
            coords.append(calculatePoint(i))
        self.draw.polygon(coords, fill=fill, outline=outline)

    def drawSquare(self, origin, size, fill=None, outline=None):
        center_x, center_y = origin

        coords = [
            (center_x - size, center_y - size),
            (center_x + size, center_y - size),
            (center_x + size, center_y + size),
            (center_x - size, center_y + size),
        ]

        self.draw.polygon(coords, fill=fill, outline=outline)

    def drawTriangle(self, origin, size, fill=None, outline=None):
        center_x, center_y = origin

        coords = [
            (center_x, center_y - size * math.sqrt(3)/3),
            (center_x - size/2, center_y + size * math.sqrt(3)/6),
            (center_x + size/2, center_y + size * math.sqrt(3)/6),
        ]

        self.draw.polygon(coords, fill=fill, outline=outline)
