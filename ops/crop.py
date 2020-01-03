from skimage.util import crop
import re

CODE = 'crop'
REGEX = re.compile(r"^" + CODE + "_(?P<y1>[-0-9]+)_(?P<y2>[-0-9]+)_(?P<x1>[-0-9]+)_(?P<x2>[-0-9]+)")

class Crop:
    def __init__(self, y1,y2,x1,x2):
        self.code = CODE +'_' + str(y1) + '_' + str(y2)+ '_' + str(x1)+ '_' + str(x2)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def process(self, img):
        return crop(img,((self.y1,self.y2),(self.x1,self.x2),(0,0)))

    @staticmethod
    def match_code(code):
        match = REGEX.match(code)
        if match:
            d = match.groupdict()
            return Crop(int(d['y1']), int(d['y2']),int(d['x1']), int(d['x2']))
