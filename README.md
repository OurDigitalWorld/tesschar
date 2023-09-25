# tesschar
Simple character checking for tesseract. The parameters are:
```
usage: tesschar.py [-h] [-f FILE] [-b BORDER] [-l LANG] [-o OUTPUT] [-t TEXT]

optional arguments:
  -h, --help            show this help message and exit

named arguments:
  -f FILE, --file FILE  input image, for example: imgs/my_image.tif
  -b BORDER, --border BORDER
                        adjust border value for extracted regions
  -l LANG, --lang LANG  language for OCR
  -o OUTPUT, --output OUTPUT
                        file for output
  -t TEXT, --text TEXT  text to reprocess
```
For example:
```
tesseract sample.jpg sample -c hocr_char_boxes=1 hocr
tesschar.py -f sample.jpg -t O,B
```
By default, the output will be in the base of the filename, _sample.txt_ in this case. Note that
a border is put around the extracted character to help improve the results. If an hocr file
is not detected, pytesseract will be used to create an in-memory version. The single character
recognition step is also done in-memory with pytesseract. This could be done more efficiently 
with the Tesseract API but the key would be to test on a big enough sample to make sure it
is worth pursuing since the process adds considerable overhead.

This has had minimal testing, YMMV, etc...
