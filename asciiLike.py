#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string, math, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

def getWindowSize():
  return (20,32)

def getCharacterImage(character, outputLines, blurFactor):
  factor = outputLines / 32
  font = ImageFont.truetype("Anonymous_Pro.ttf",32*factor)
  img = Image.new("RGB", (20*factor,32*factor),(0,0,0))
  draw = ImageDraw.Draw(img)
  draw.text((2.5*factor, -3*factor),character,(255,255,255),font=font)
  return img.filter(ImageFilter.GaussianBlur(blurFactor))

def getReferenceImages(outputLines):
  allowedChars = string.printable
  references = {}
  for char in allowedChars:
    references[char] = getCharacterImage(char, outputLines, 2.25)
  return references

def getBestFitChar(image, referenceImages):
  bestScore = None
  bestKey = None
  for (char, reference) in referenceImages.iteritems():
    distance = getImageDifference(image, reference)
    if bestScore == None or distance < bestScore:
      bestScore = distance
      bestKey = char
  return (bestKey, bestScore)

def getImageDifference(imgA, imgB):
  a = getImagePixels(imgA)
  b = getImagePixels(imgB)
  diff_squares = [(a[i] - b[i]) ** 2 for i in xrange(len(a))]
  return math.sqrt(sum(diff_squares) / len(a));

def getImagePixels(image):
  colorData = list(image.getdata())
  pixels = [i[j] for i in colorData for j in range(len(i))]
  return pixels

# def dilate(image):
#   img = cv2.imread('j.png',0)
#   kernel = np.ones((5,5),np.uint8)
#   erosion = cv2.erode(img,kernel,iterations = 1)

def convertImageForProcessing(image, outputLines):
  image = resizeToOutput(image, outputLines, 32)
  image = ImageOps.grayscale(image)
  enhancer = ImageEnhance.Contrast(image)
  image = enhancer.enhance(1.3)
  enhancer = ImageEnhance.Brightness(image)
  image = enhancer.enhance(0.3)
  # image = ImageOps.equalize(image)
#  image = image.filter(ImageFilter.FIND_EDGES)
  # image = ImageOps.invert(image)
  image = paddToEvenRows(image)
  return image

def resizeToOutput(image, outputLines, pixelsPerLine):
  (inputX, inputY) = image.size
  processingY = outputLines * pixelsPerLine
  processingFactor = float(processingY) / float(inputY)
  processingX = int(float(inputX) * processingFactor)
  return image.resize((processingX, processingY), Image.ANTIALIAS)

def paddToEvenRows(image):
  print str(image.size)
  padded = Image.new('RGB', getRoundedDimensions(image.size))
  padded.paste(image, image.getbbox())
  print str(padded.size)
  return padded

def getRoundedDimensions((x,y)):
  (wx,wy) = getWindowSize()
  nx = int(math.ceil(float(x)/float(wx)) * wx)
  ny = int(math.ceil(float(y)/float(wy)) * wy)
  return (nx,ny)

def convertToAscii(image, outputLines):
  result = ""
  referenceImages = getReferenceImages(outputLines)
  image = convertImageForProcessing(image, outputLines)

  (wx,wy) = getWindowSize()
  (ix,iy) = image.size
  for y in range(0, iy, wy):
    for x in range(0, ix, wx):
      box = (x, y, x+wx, y+wy)
      region = image.crop(box)
      (char, score) = getBestFitChar(region, referenceImages)
      result += char
    result += "\n"
  return result

img = Image.open('ham.jpg')
# img = img.resize((200, 200), Image.ANTIALIAS)
img.show()
convertImageForProcessing(img,32).show()
print str(convertToAscii(img, 32))
