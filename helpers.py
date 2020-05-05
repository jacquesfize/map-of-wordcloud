import re

import numpy as np

from skimage.color import rgb2gray
from skimage import measure
from skimage.io import imread

from PIL import Image


import string
import random


def find_contour(mask_rgb):
    img = rgb2gray(mask_rgb)
    contours = measure.find_contours(img, 0.8)
    return contours

def contours_to_polygon_svg(contours,color="white"):
    poly_str = ""
    for contour in contours:
        points_str= " ".join(["{0},{1}".format(c[1],c[0]) for c in contour]) # lat and lon so inverse order is required
        poly_str+="""\n<polygon points="{0}" style="fill-opacity:0;fill:lime;stroke:{1};stroke-width:1" />\n""".format(points_str,color)
    return poly_str

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def get_img_from_fig(fig,random_png_filename,dpi=360):
    fig.savefig(random_png_filename, format="png", dpi=dpi,bbox_inches='tight', pad_inches=0)
    a = np.array(Image.open(random_png_filename).convert("L"))
    a[a < 255] = 0
    return a

def single_color(word=None, font_size=None, position=None,orientation=None, font_path=None, random_state=None):
    return "rgb(255,255,255)"

def extract_svg_content(svg):
    svg = re.sub(r"<svg[^>]*>","",svg)
    svg = re.sub(r"</svg[^>]*>","",svg)

    svg=re.sub(r"<style[^>]*>[^<]+</style>","",svg)
    svg=re.sub(r"<rect[^>]*></rect>","",svg)
    return svg