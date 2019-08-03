## Chris Bowers
## 8 July 2019
## Final version of the RCK screenshot program

## Known issues:
### Will error with 'tile cannot extend outside image' if entire comment does not fit

## Crops single reddit comment screenshot given url
from selenium import webdriver
from PIL import Image
from PIL import ImageColor
import numpy as np
import os as os
import image_processing_rck as ip

# get comment urls from text document list
url_file = open('comment_urls', 'r')
urls = url_file.readlines()

# get screenshots of all reddit comments in url text document
comment_sc_inc = 0
sc_name = [0] * len(urls)
for url in urls:
    print('Capturing screenshot  ' + str(comment_sc_inc) + '  of  ' + str(len(urls)))
    DRIVER = '/home/chris/Documents/python/read_reddit/chromedriver'
    driver = webdriver.Chrome(DRIVER)
    driver.get(url)
    sc_name[comment_sc_inc] = 'reddit_comment_orignal' + str(comment_sc_inc) + '.png'
    sc = driver.save_screenshot(sc_name[comment_sc_inc])
    driver.quit()
    comment_sc_inc += 1

# crop down individual screenshots
comment_inc = 0
cropped_sc_name = [0] * len(urls)
while comment_inc < len(urls):

    print('Reddit Comment Num: ' + str(comment_inc) + '\n')
    # open image and get max width and height
    comment_sc = Image.open(sc_name[comment_inc])
    sc_width, sc_height = comment_sc.size
    print(comment_sc.filename)
    print('width: ' + str(sc_width))
    print('height: ' + str(sc_height))

    # this array maybe imported as an array, causing for a 3D array where:
    # 1D row array running down y axis by 1 pixel row per element
    # 2D pixel array for each pixel on x axis
    # 3D each RGBA value
    # ie: pix_array[238][20][2] is the Blue value at pixel (20, 238)
    pix_array = np.asarray(comment_sc)
    ##print(pix_array[0])
    ##print(pix_array[0][0])
    ##print(pix_array[0][0][0])

    # determines if header is present, if so will elimate all pixel data from header
    header_present, header_height = ip.headerPresent(pix_array)
    #print('header height' + str(header_height))
    ##if header_present:
    ##    inc = 0
    ##    while inc < len(pix_array):
    ##        print(pix_array[inc])
    ##        pix_array[inc] = pix_array[header_height + inc]
    ##        print(pix_array[inc])
    ##        inc += 1

    # find longest grey streak below the header
    inc = 0
    pix_y_inc = 0
    grey_len_inc = 0
    white = [255, 255, 255]
    comment_grey = [245, 246, 246]
    black = [0, 0, 0]
    prev_grey = False
    grey_len = np.zeros((sc_width * sc_height, 3))
    for pix_y in pix_array:
        pix_x_inc = 0
        for pix_x in pix_y:
            if (
                ip.isColor(pix_x, comment_grey) and
                grey_len[grey_len_inc][0] == 0            
               ):
                grey_len[grey_len_inc][0] = 1
                grey_len[grey_len_inc][1] = pix_x_inc
                grey_len[grey_len_inc][2] = pix_y_inc
                prev_grey = True
            elif ip.isColor(pix_x, comment_grey):
    ##            print(grey_len_inc)
    ##            print(grey_len[grey_len_inc])
                grey_len[grey_len_inc][0] += 1
                prev_grey = True
            elif prev_grey == True:
                grey_len_inc += 1
                prev_grey = False
            pix_x_inc += 1
        pix_y_inc += 1        

    # grey_len trim
    grey_len_trim = ip.trimArray(grey_len, grey_len_inc, 3, 'row')
    #ip.longPrint(grey_len_trim, 0, 15)

    ### grey_len max len
    grey_len_max, max_loc = ip.colMax(grey_len_trim, 0, len(grey_len_trim))
    #print(max_loc)
    #print(grey_len_trim[max_loc])

    comment_sc_crop = comment_sc.crop((grey_len_trim[max_loc][1],
                                  grey_len_trim[max_loc][2],
                                  grey_len_trim[max_loc][1] + grey_len_trim[max_loc][0],
                                  sc_height))

    # this array maybe imported as an array, causing for a 3D array where:
    # 1D row array running down y axis by 1 pixel row per element
    # 2D pixel array for each pixel on x axis
    # 3D each RGBA value
    # ie: pix_array[238][20][2] is the Blue value at pixel (20, 238)
    pix_array_comment = np.asarray(comment_sc_crop)
    ##print(pix_array[0])
    ##print(pix_array[0][0])
    ##print(pix_array[0][0][0])

    # find the 599 length grey streaks and black out the bottom from there
    # grey_spans_trim:
    #  grey_spans_trim[row_val] | Row of grey blanks found in comment section with
    #                             height greater than or equal to the section's max
    #                             length - 30 pixels.
    #                             If comments are getting cut off, change number of
    #                             pixels used in uncertainty.
    #  grey_spans_trim[row_val][0] | Number of comment background colored pixels in
    #                                a row.
    #  grey_spans_trim[row_val][1] | x position of start of streak
    #  grey_spans_trim[row_val][2] | y position of start of streak
    grey_spans, grey_spans_inc = ip.findGreyBlanks(grey_len_trim, grey_len_trim[max_loc][0])
    grey_spans_trim = ip.trimArray(grey_spans, grey_spans_inc, 3, 'row')

    # find the cut points between comment lines
    comment_cuts, comment_cuts_inc = ip.commentSpaceHalfPosition(grey_spans_trim, grey_len_trim[max_loc][2])
    comment_cuts_trim = ip.trimArray(comment_cuts, comment_cuts_inc, 3, 'row')

    # sets folder name
    folder_name = 'comment_scs'
    if os.system('mkdir ' + folder_name) == 256:
        os.system('rm ' + folder_name)
        os.system('mkdir ' + folder_name)
    
    cropped_sc_name[comment_inc] = 'full_comment_' + str(comment_inc) + '.png'
    comment_sc_crop.save(folder_name + '/' + cropped_sc_name[comment_inc])

    # debug crops with cropped image
    inc = 0
    print(comment_cuts_trim)
    while inc < len(comment_cuts_trim):
        print('Image ' + str(comment_inc) + '.' + str(inc) + ' saving...')
        ip.quickCropCropped(0,
                            0,
                            grey_len_trim[max_loc][0],
                            comment_cuts_trim[inc][0],
                            cropped_sc_name[comment_inc],
                            folder_name,
                            comment_inc,
                            inc)
        inc += 1

    comment_inc += 1
