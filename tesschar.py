"""
tesschar.py - use single character recognition on glyphs

Usage (see list of options):
    tesschar.py [-h] 

For example:
    tesschar.py -f test.jpg
    tesschar.py -f test.jpg -t O,o

- art rhyno, u. of windsor & ourdigitalworld
"""

import xml.etree.ElementTree as ET
import argparse, glob, math, os, sys
from pytesseract import pytesseract, Output
from PIL import Image

#namespace for HOCR
HOCR_NS = 'http://www.w3.org/1999/xhtml'
ET.register_namespace('html', HOCR_NS)

""" pull coords and sometimes conf from bbox string """
def getBBoxInfo(bbox_str):
    conf = None

    if ';' in bbox_str:
        bbox_info = bbox_str.split(';')
        bbox_info = bbox_info[1].strip()
        bbox_info = bbox_info.split(' ')
        conf = float(bbox_info[1])
    bbox_info = bbox_str.replace(';',' ')
    bbox_info = bbox_info.split(' ')
    x0 = int(bbox_info[1])
    y0 = int(bbox_info[2])
    x1 = int(bbox_info[3])
    y1 = int(bbox_info[4])

    return x0,y0,x1,y1,conf

""" use Hocr structure for identifying chars and probs """
def runThruHocr(ifile,hsource,iborder,clist,output):

    print("work through hocr...",end="",flush=True)
    subs = 0
    out_file = open(output, "w")
    started = False
    word_started = False
    img = Image.open(ifile)

    if os.path.exists(hsource):
        tree = ET.ElementTree(file=hsource)
    else:
        tree = ET.ElementTree(ET.fromstring(hsource))

    for elem in tree.iterfind('.//{%s}%s' % (HOCR_NS,'p')):
        if 'class' in elem.attrib:
            class_name = elem.attrib['class']
            if class_name == 'ocr_par': 
                words = ''
                for span_elem in elem.iterfind('.//{%s}%s' % (HOCR_NS,'span')):
                    class_name = span_elem.attrib['class']
                    if class_name == 'ocr_line' or class_name == 'ocr_textfloat':
                        if started:
                            out_file.write("\n")
                        started = True
                        word_started = False
                    if class_name == 'ocrx_word': #word details
                        if word_started:
                            out_file.write(" ")
                        word_started = True
                        print(".",end="",flush=True)
                    if class_name == 'ocrx_cinfo': 
                        x0,y0,x1,y1,conf = getBBoxInfo(span_elem.attrib['title'])

                        if span_elem.text in clist:
                            rw = (x1 - x0) + iborder
                            rh = (y1 - y0) + iborder
                            im_w_border = Image.new("RGB",[rw,rh],color="white")
                            pg_box = (x0,y0,x1,y1)
                            roi_rect = img.crop(pg_box)
                            adj = round(iborder/2)
                            im_w_border.paste(roi_rect,(adj,adj))
                            """
                            for debugging
                            im.save("imgs/%s_%d_%d_%d_%d.jpg" % (span_elem.text,
                                x0,y0,x1,y1))
                            """
                            tdata = pytesseract.image_to_data(im_w_border, 
                                    config='--psm 10',
                                    output_type=Output.DICT)

                            """
                            confidence would be useful here but seems to be
                            off for single character recognition, e.g.
                            new_conf = float(tdata['conf'][-1])
                            """
                            out_file.write(tdata['text'][-1])
                            subs += 1
                        else:
                            out_file.write(span_elem.text)
    out_file.close()
    print("!")

    return subs

parser = argparse.ArgumentParser()
arg_named = parser.add_argument_group("named arguments")
arg_named.add_argument("-f","--file", 
    help="input image, for example: imgs/my_image.tif")
arg_named.add_argument("-b","--border", default=10, type=int,
    help="adjust border value for extracted regions")
arg_named.add_argument('-l', '--lang', type=str, 
    default="eng",
    help="language for OCR")
arg_named.add_argument('-o', '--output', type=str, 
    help="file for output")
arg_named.add_argument('-t', '--text', type=str, 
    default="O,B",
    help="text to reprocess")

args = parser.parse_args()

if args.file == None or not os.path.exists(args.file):
    print("missing input image, use '-h' parameter for syntax")
    sys.exit()

#use filename to pull everything together
parts = args.file.split(".")
if len(parts) > 1:
    parts.pop()
img_base = ".".join(parts)

if args.output == None:
    args.output = img_base + ".txt"

orig_page = img_base + ".hocr"
if not os.path.exists(orig_page):
    print("missing base hocr file: %s.hocr, running Tesseract" % img_base)
    orig_page = pytesseract.image_to_pdf_or_hocr(args.file,
        config=("-l %s -c hocr_char_boxes=1" % args.lang),
        extension='hocr')

subs = runThruHocr(args.file,orig_page,args.border,args.text,args.output)
print("substitutions", subs)
