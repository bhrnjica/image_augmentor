import numpy
from PIL import Image
import re

CODE = 'resize'
REGEX = re.compile(r"^" + CODE + "_(?P<h>[.0-9]+)"+ "_(?P<w>[.0-9]+)")

class Resize:
    def __init__(self, high, width):
        self.code = CODE + str(high) + str(width)
        self.high = high
        self.width = width

   # def process(self, img):
       # return fix_size(fn=img,desired_w= self.width, desired_h=self.high)

    def process(self, img):
        #(self, fn, desired_w=256, desired_h=256, fill_color=(0, 0, 0, 255)):
        """Edited from https://stackoverflow.com/questions/44231209/resize-rectangular-image-to-square-keeping-ratio-and-fill-background-with-black"""
        fill_color=(255,255,255)
        im = Image.fromarray(img, mode= "RGB")
        x, y = im.size

        ratio = x / y
        desired_ratio = self.width / self.high

        w = max(self.width, x)
        h = int(w / desired_ratio)
        if h < y:
            h = y
            w = int(h * desired_ratio)

        new_im = Image.new('RGB', (w, h), fill_color)
        new_im.paste(im, ((w - x) // 2, (h - y) // 2))
        resized = new_im.resize((self.width, self.high))
        data = numpy.asarray(resized)
        return  data

    @staticmethod
    def match_code(code):
        match = REGEX.match(code)
        if match:
            d = match.groupdict()
            return Resize(int(d['h']),int(d['w']))
