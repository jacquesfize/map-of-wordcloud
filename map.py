from os import path
import os
import argparse
import json
import string
import random
import re

import geopandas as gpd
import numpy as np

import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

from tqdm import tqdm

from helpers import *


random_png_filename = randomString()+".png"

parser = argparse.ArgumentParser()
parser.add_argument("shapefile")
parser.add_argument("column_used")
parser.add_argument("count_data_filename")
parser.add_argument("output_filename")
parser.add_argument("-f","--format",default="pdf",choices=["html","png","pdf"])
parser.add_argument("--dpi",type=int,default=360)

args = parser.parse_args()#"france_metropolitaine code_insee wikipedia_dep.json wikipedia2.png".split())

if not os.path.exists(args.shapefile):
    raise FileNotFoundError("{0} does not exists !".format(args.shapefile))

if not os.path.exists(args.count_data_filename):
    raise FileNotFoundError(
        "{0} does not exists !".format(args.count_data_filename)
    )

gdf = gpd.read_file(args.shapefile)
count_data = json.load(open(args.count_data_filename))
column_selected = args.column_used
is_svg = (True if args.format in ("html","pdf") else False)
is_pdf = (True if args.format =="pdf" else False)

if not column_selected in gdf:
    raise KeyError("{0} does not exists in the data !".format(column_selected))


image_finale = None

svg=None
header = ""

i = 0
for x in tqdm(gdf[column_selected].values[:4]):
    if not x in count_data:
        continue
    
    # EXTRACT MASK FORMED BY THE POLYGON GEOMETRY
    fig, ax = plt.subplots(1)
    # PLOT ALL DATAFRAME TO HAVE MATRIX OF SAME SIZE AT EACH LOOP
    gdf.plot(color="white", ax=ax)
    # PLOT PARTICULAR SUBSET BASED ON INDICATED COLUMN
    gdf[gdf[column_selected] == x].plot(color="black", ax=ax)
    plt.axis("off")
    mask_geo = get_img_from_fig(fig,random_png_filename, dpi=args.dpi)

    # INITIALISE WORDCLOUD GENERATOR
    wc = WordCloud(
        background_color="rgb(125,125,125)",
        max_words=2000,
        mask=mask_geo,
        stopwords=[],
        contour_width=3,
        contour_color="black",
        #font_path="./Jost/Jost-VariableFont_ital,wght.ttf",
        color_func=single_color
    )
    
    # GENERATE THE WORDCLOUD
    try: # Not enough place in mask canvas can cause errors
        wc.generate_from_frequencies(count_data[x])
        if is_svg:
            curr_ = wc.to_svg()
        else:
            wc.to_file(random_png_filename)
    except:
        svg+="\n"+contours_to_polygon_svg(find_contour(mask_geo))+"\n"
        continue

    #Get WordCloud matrix/or vectors
    if i == 0:
        if is_svg:
            header += re.findall(r"<svg[^>]*>",curr_)[0]
            header += re.findall(r"<style[^>]*>[^<]+</style>",curr_)[0]
            header += re.findall(r"<rect[^>]*></rect>",curr_)[0]
            svg = extract_svg_content(curr_)
        else:
            image_finale = wc.to_array()
        i += 1
    else:
        if is_svg:
            svg += extract_svg_content(curr_)
        else:
            image_finale = image_finale + wc.to_array()

    #postreatment
    if not is_svg:
        image_finale[image_finale == [255, 255, 255]] = 0
    else:
        svg+="\n"+contours_to_polygon_svg(find_contour(mask_geo))+"\n"

    plt.close("all")# TO AVOID RAM CONSUMPTION

if is_svg:
    svg = header + svg + "\n</svg>"
    open(args.output_filename,'w').write(svg)
else:
    image_finale[image_finale == [0, 0, 0]] = 255

    plt.imshow(image_finale)
    plt.axis("off")
    plt.savefig(args.output_filename,dpi=args.dpi)

if is_svg and is_pdf:
    import cairosvg
    cairosvg.svg2pdf(url=args.output_filename, write_to=args.output_filename)
os.remove(random_png_filename)
