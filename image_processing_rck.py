# module for image_processing of websites
## This module is unstable, there seems to be an issue with passing the colors array
from selenium import webdriver
from PIL import Image
from PIL import ImageColor
import numpy as np

# determines whether header is present in image
def headerPresent(pix_array):
    isPresent = False
    light_blue = [240, 247, 253]
    header_grey = [68, 78, 89]
    inc = 0
    end_of_blue = 0
    for pix_zero_x in pix_array:
        if (isColor(pix_zero_x[inc], light_blue) or isColor(pix_zero_x[inc], header_grey)):
##            print(pix_zero_x[inc])
            isPresent = True
            if end_of_blue == 0:
                end_of_blue += inc
            end_of_blue += 1
        inc += 1
##    print('pix_zero_x value ends with: ' + str(pix_zero_x[inc]))
    return isPresent, end_of_blue

# finds space between comment lines
# takes: grey_spans | grey_spans array produced from ip.findGreyBlanks()
# gives: comment_bot_height | array of inbetween heights on comment lines
#       comment_bot_height[row_val] is row of location data
#       comment_bot_height[row_val][0] is pixel height for cropped image
#       comment_bot_height[row_val][1] is pixel height for start of space between lines
#       comment_bot_height[row_val][2] is pixel height for end of space between lines
def commentSpaceHalfPosition(grey_spans, comment_start_height):
    inc = 1
    csh_inc = 0
    is_streak = False
    comment_segment_height = np.zeros((len(grey_spans), 3))
    while inc < len(grey_spans) - 1:
        if (grey_spans[inc][2] == (grey_spans[inc-1][2] + 1) and
            comment_segment_height[csh_inc][1] == 0):
            comment_segment_height[csh_inc][1] = grey_spans[inc-1][2]
##            print(comment_segment_height[csh_inc][1])
            is_streak = True
        elif grey_spans[inc][2] == (grey_spans[inc-1][2] + 1):
            comment_segment_height[csh_inc][2] = grey_spans[inc-1][2]
            comment_segment_height[csh_inc][0] = np.ceil(comment_segment_height[csh_inc][2] - ((comment_segment_height[csh_inc][2] - comment_segment_height[csh_inc][1]) / 2)) - comment_start_height
##            print('thing' + str(comment_segment_height[csh_inc][0]))
        elif is_streak == True:
##            print('streak end')
            csh_inc += 1
            is_streak = False
##        print(str(inc) + '/' + str(len(grey_spans)))
##        print(csh_inc)
        inc += 1

    csh_inc += 1
    print(grey_spans[inc-1])
    print(colAvg(comment_segment_height, 0, inc+1))
    comment_segment_height[csh_inc][1] = grey_spans[inc][2]
    comment_segment_height[csh_inc][2] = grey_spans[inc-1][2] + colAvg(comment_segment_height, 0, inc+1)
    comment_segment_height[csh_inc][0] = np.ceil(comment_segment_height[csh_inc][2] - ((comment_segment_height[csh_inc][2] - comment_segment_height[csh_inc][1]) / 2)) - comment_start_height
    return comment_segment_height, csh_inc

# calculates average of a particular column
# takes: arr | array to calculate average from
#        col_num | column to calculate average of
#        num_vals | number of rows to consider
# gives: avg | average value of given column
def colAvg(arr, col_num, num_vals):
    inc = 0
    avg = 0
    while inc < num_vals:
        avg += arr[inc][col_num]
        inc += 1
    avg /= num_vals
    return avg

# prints less truncated numpy array
# takes: arr | array to be printed
#        start_val | index to start printing from
#        num_prints | number of values to be printed
def longPrint(arr, start_val, num_prints):
    for inc in range(start_val, start_val + num_prints):
        print(arr[inc])

# gets a screenshot of as much of a website as fits in a default window size chrome window
# takes: url | url of website to be screenshot
# gives: sc_name | save name of screenshot image png
#
# may add option to give sc_name?
#
def getScreenshot(url):
    DRIVER = '/home/chris/Documents/python/read_reddit/chromedriver'
    driver = webdriver.Chrome(DRIVER)
    driver.get(url)
    sc_name = 'reddit_comment_orignal.png'
    sc = driver.save_screenshot('reddit_comment_orignal.png')
    driver.quit()
    return sc_name

# finds locations where color has changed between horizontal pixels
# takes: sc_height | total height of screenshot
#        sc_width | total width of screenshot
# gives: colors_trim | trimmed array with all color changes, and the location of the change
#        num_color_changes | number of changes in color, useful for trimming data
def getColorChanges(pix_array, sc_height, sc_width):
    num_color_changes = 0
    pixel_location = 0
    pixel_height = 0
    colors = np.empty((sc_height * sc_width, 6))
    pix_x_prev = [-1, -1, -1, -1]
    pixel_y_loc = 0
    for pix_y in pix_array:
        pixel_x_loc = 0
        for pix_x in pix_y:
            #print(pixel_location)
            #print('pix_x is ' + str(pix_x))
            #print('prev      is ' + str(pix_x_prev))
            # check if color is not same as previous
            if (
               not (pix_x == pix_x_prev)[0] and
               not (pix_x == pix_x_prev)[1] and
               not (pix_x == pix_x_prev)[2]
               ):
               for i in range(0, 4):
                   colors[num_color_changes][i] = pix_x[i]
               colors[num_color_changes][4] = pixel_x_loc
               colors[num_color_changes][5] = pixel_y_loc
               num_color_changes += 1
            pix_x_prev = pix_x
            pixel_x_loc += 1
        pixel_y_loc += 1
        
    # trim trailing zeros
    colors_trim = np.empty((num_color_changes, 6))
    for k in range(0, num_color_changes):
        colors_trim[k] = colors[k]
    #print(colors_trim)
    return colors_trim, num_color_changes

# determines if color is unique compared to those listed in array
# takes: found_unique_colors | colors that have already been found in image
#        pixel | RGB value in 3 element array
#        pix_current_row | current row in pixel
# gives: is_unique | true if pixel color is not already in found_unique_colors
def uniqueColor(found_unique_colors, pixel):
    inc = 0
    is_unique = True
    for unique_color in found_unique_colors:
        if (
            pixel[0] == unique_color[0] and
            pixel[1] == unique_color[1] and
            pixel[2] == unique_pixel[2]
           ):
            is_unique = False
            break
        inc += 1
    return is_unique

# determines if a pixel is of a specific color
# takes: pixel | RGB value in 3 element array
#        color | RGB value to be compared against in 3 element array
# gives: is_color | true if pixel value matches color value
def isColor(pixel, color):
    is_color = False
    if (
        pixel[0] == color[0] and
        pixel[1] == color[1] and
        pixel[2] == color[2]
       ):
        is_color = True
    return is_color

# determines if a pixel is monochrome
# takes: pixel | RGB value in 3 element array
# gives: is_mono | true if pixel is monochrome
def isMono(pixel):
    is_mono = False
    if (
        pixel[0] == pixel[1] and
        pixel[1] == pixel[2]
       ):
        is_mono = True
    return is_mono

# trims unwritten array elements
# takes: arr | the array to get data from
#        rows | rows to be used
#        cols | columns to be used (1 if array is 1D)
#   rows and cols must be same as arr_trim
#        row_col | whether row or column is to be iterated through
# gives: arr_trim | trimmed array
def trimArray(arr, rows, cols, row_col):
    arr_trim = np.empty((rows, cols))
    if row_col == 'row':
        for inc in range(0, rows):
            arr_trim[inc] = arr[inc]
    elif row_col == 'col':
        for inc in range(0, col):
            arr_trim[inc] = arr[inc]
    return arr_trim

# obtains array of monochrome streaks and their lengths in image
# takes: color_array | array of color changes in an image
#        num_color_changes | number of color changes in image
# gives: grey_len_trim | trimmed array of all streaks of grey, their length, and where they start
#           0D is length of grey streak
#           1D is x position of grey streak start
#           2D is y position of grey streak start
def longestHorzMonoStreak(color_array, num_color_changes):
    inc = 0
    grey_len_inc = 0
    white = [255, 255, 255]
    black = [0, 0, 0]
    prev_mono = False
    grey_len = np.empty((num_color_changes, 3))
    while inc < num_color_changes:
##        print(color_array[inc])
        if (
            isMono(color_array[inc]) and
            not isColor(color_array[inc], white) and
            not isColor(color_array[inc], black)
           ):
            grey_len[grey_len_inc][0] += 1
            prev_mono = True
##            print(str(grey_len_inc) + ' is mono')
##            print(grey_len[grey_len_inc])
            if grey_len[grey_len_inc][0] == 1:
                grey_len[grey_len_inc][1] = color_array[inc][4]
                grey_len[grey_len_inc][2] = color_array[inc][5]
        elif prev_mono:
            grey_len_inc += 1
            prev_mono = False
##            print(str(grey_len_inc) + ' is not mono')
##            print(grey_len[grey_len_inc])
        inc += 1
    ## print(len(grey_len))

    # trims off unused array elements
    grey_len_trim = trimArray(grey_len, grey_len_inc, 3, 'row')
    return grey_len_trim
                        
# determines the max value of one column of an array
# takes: arr | the array the max is to be found in
#        col | the column the max is to be found in
#        arr_max | max size of the array
# gives: max_val | maximum value found in the column, -1 by default
#        loc | element number where max value was found
def colMax(arr, col, arr_max):
    max_val = -1
    inc = 1
    loc = -1
    while inc < arr_max:
        if arr[inc][col] > max_val:
##            print(str(arr[inc][col]) + '>' + str(arr[inc-1][col]))
            max_val = arr[inc][col]
            loc = inc
        inc += 1
    return max_val, loc

# finds all comment_grey streaks spanning the length of the comment box or - 30 of len
# takes: comment_array | array of pixels making up the comment box
#        box_len | length of comment box, usually given by grey_len_trim[max_loc][0]
# gives: grey_spans | all streaks of grey that span the length of the comment box
#        inc | amount of data written to grey_spans
def findGreyBlanks(comment_array, box_len):
    inc = 0
    grey_spans = np.empty((len(comment_array), 3))
    for pix in comment_array:
        # Greater than minus 30 for the left side collapsing grey bar
        if pix[0] >= (box_len - 30):
            grey_spans[inc] = pix
            inc += 1
    return grey_spans, inc
            

# quick cropping tool for debugging
def quickCrop(left, top, right, bot, num):
    sc_name = 'reddit_comment_orignal.png'

    # open image and get max width and height
    comment_sc = Image.open(sc_name)    
    comment_sc = comment_sc.crop((left,
                                  top,
                                  right,
                                  bot))
    comment_sc.save()

# quick tool for cropping the comment screenshot
def quickCropCropped(left, top, right, bot, sc_name, folder_name, comment_num, num):
    # open image and get max width and height
    comment_sc = Image.open(folder_name + '/' + sc_name)    
    comment_sc = comment_sc.crop((left,
                                  top,
                                  right,
                                  bot))
    comment_sc.save(folder_name + '/' + 'comment_sc_' + str(comment_num) + '_crop_' + str(num) + '.png')

def quickCropBox(x_center, y_center, num):
    sc_name = 'reddit_comment_orignal.png'

    # open image and get max width and height
    comment_sc = Image.open(sc_name)
    sc_width, sc_height = comment_sc.size
    
    comment_sc = comment_sc.crop((x_center - 20,
                                  y_center - 20,
                                  x_center + 20,
                                  y_center + 20))
    comment_sc.save('box' + str(num) + '.png')
