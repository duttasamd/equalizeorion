import csv
import numpy as np
import collections
from PIL import Image
from PIL import ImageDraw
import matplotlib.pyplot as plt


def parseinputimage(filename):

    """
    :param filename:filepath. File should contain a 500*500 image data,
                    each datapoint in quotes and separated by a ','
    :return: imgarr : 2D array of floating points parsed from the file,
             histdict: A dictionary of each value paired with the number of occurances,
             maxrow : row number containing the maximum value
    """

    histdict = {}
    imgarr = [None for y in range(500)]
    count = 0
    _max = 0
    _maxrow = 0

    with open(filename, "r") as f:
        for row in csv.reader(f, delimiter=',', skipinitialspace=True):
            imgrow = []
            for point in row:
                fpoint = float(point)

                if fpoint > _max:
                    _max = fpoint
                    _maxrow = count
                imgrow.append(fpoint)
                if fpoint not in histdict:
                    histdict[fpoint] = 1
                else:
                    histdict[fpoint] += 1
            imgarr[count] = imgrow
            count += 1

    return imgarr, histdict,_maxrow


def equalizeimg(histdict, img, _max) :
    ordereddict = collections.OrderedDict(sorted(histdict.items()))
    eqdict = {}
    prevprob = 0
    for key in ordereddict:
        prob = ordereddict[key] / (500 * 500)
        prob += prevprob
        prevprob = prob
        eqdict[key] = int(round(prob * _max))

    equalizedimg = [None for y in range(500)]

    for i in range(500):
        eqrow = []
        for j in range(500):
            point = img[499 - i][j]
            eqrow.append(eqdict[point])
        equalizedimg[i] = eqrow

    return equalizedimg


def lineartransform(rawimage) :
    eqimg = np.asarray(rawimage)
    c2 = eqimg.min()
    c1 = 255 / eqimg.max()

    linearTimg = [None for y in range(500)]

    for i in range(500):
        linearrow = []
        for j in range(500):
            linearrow.append(int(round(eqimg[i][j] * c1 + c2)))

        linearTimg[i] = linearrow

    return linearTimg


def processfile(filename):
    imgarr, histdict, _maxrow = parseinputimage(filename)
    img = np.asarray(imgarr)
    _max = img.max()

    eqimg = equalizeimg(histdict, img, _max)

    transImage = lineartransform(eqimg)
    limg = np.asarray(transImage)
    im = Image.fromarray(limg.astype(float))

    return im


def processtolimg(filename):
    imgarr, histdict, _maxrow = parseinputimage(filename)
    img = np.asarray(imgarr)
    _max = img.max()

    eqimg = equalizeimg(histdict, img, _max)

    transImage = lineartransform(eqimg)
    limg = np.asarray(transImage)

    return limg


def combinechannelstorgb(red, green, blue):
    image = []
    for i in range(500):
        for j in range(500):
            image.append(tuple([red[i][j], green[i][j], blue[i][j]]))

    return image


# ======================================== SCRIPT ==================================================================


img2arr, histdict2, _maxrow = parseinputimage("res/i170b2h0_t0.txt")
img2 = np.asarray(img2arr)
_max = img2.max()

print("Data characteristics for band 2: ")
print("Min :", img2.min(), ", Max :", img2.max())
print("Mean :", img2.sum()/(512*512))
print("Variance :", np.var(img2, ddof=1))

plt.plot(list(range(500)), img2arr[_maxrow], "-o")
plt.ylabel('Position');
plt.xlabel('Values');
plt.savefig("out/profileline.png")

lineartransformedimg2 = lineartransform(img2)
limg2 = np.asarray(lineartransformedimg2)
im = Image.fromarray(limg2.astype(float))
im = im.convert("L")
im.save("out/non-equalizedraworion.png", "png")

eqimg2 = equalizeimg(histdict2, img2arr, _max)
transImage2 = lineartransform(eqimg2)
limg2 = np.asarray(transImage2)
im2 = Image.fromarray(limg2.astype(float))

# im2.show()

# process the rest of the files and obtain the final image to be displayed.
im1 = processfile("res/i170b1h0_t0.txt")
im3 = processfile("res/i170b3h0_t0.txt")
im4 = processfile("res/i170b4h0_t0.txt")

# combine the 4 equalized images into one image with white background.
combinedim = Image.new("L", (1090,1090), 255)

combinedim.paste(im1, (30,30))
combinedim.paste(im2, (30,560))
combinedim.paste(im3, (560,30))
combinedim.paste(im4, (560,560))

# label the images
draw = ImageDraw.Draw(combinedim)
draw.text((250, 15),"Band 1",fill="black")
draw.text((780, 15),"Band 2",fill="black")
draw.text((250, 545),"Band 3",fill="black")
draw.text((780, 545),"Band 4",fill="black")

# combinedim.show()
combinedim.save("out/equalized.png", "png")


#TODO : [Remove inefficiency] Plan the function structures better. The following block has already been computed.
blue = processtolimg("res/i170b1h0_t0.txt")
green = processtolimg("res/i170b3h0_t0.txt")
red = processtolimg("res/i170b4h0_t0.txt")

# combine the equalized and transformed RGB channels into a single RGB image.
rgbtuplelist = combinechannelstorgb(red, green, blue)

rgbim = Image.new("RGB", (500,500))
rgbim.putdata(rgbtuplelist)

rgbim.save("out/rgborion.png", "png")


