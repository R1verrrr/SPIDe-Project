import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import cv2
from . import dataset



from numba import jit

# Function to preprocess neighbors (small_window x small_window) for each pixel
@jit(nopython=True, cache=True)
def findAllNeighbors(padImg,small_window,big_window,h,w):
    # Finding width of the neighbor window and padded image from the center pixel
    smallWidth = small_window//2
    bigWidth = big_window//2

    # Initializing the result
    neighbors = np.zeros((padImg.shape[0],padImg.shape[1],small_window,small_window))

    # Finding the neighbors of each pixel in the original image using the padded image
    for i in range(bigWidth,bigWidth + h):
        for j in range(bigWidth,bigWidth + w):   
            neighbors[i,j] = padImg[(i - smallWidth):(i + smallWidth + 1) , (j - smallWidth):(j + smallWidth + 1)]
    
    return neighbors

# Function to calculate the weighted average value (Ip) for each pixel
@jit(nopython=True, cache=True)
def evaluateNorm(pixelWindow, neighborWindow, Nw):
    # Initialize numerator and denominator of Ip (Ip = Ip_Numerator/Z)
    Ip_Numerator,Z = 0,0

    # Calculating Ip for pixel p using neighborood pixels q
    for i in range(neighborWindow.shape[0]):
      for j in range(neighborWindow.shape[1]):
        # (small_window x small_window) array for pixel q
        q_window = neighborWindow[i,j]

        # Coordinates of pixel q
        q_x,q_y = q_window.shape[0]//2,q_window.shape[1]//2

        # Iq value
        Iq = q_window[q_x, q_y]

        # Norm of Ip - Iq
        w = np.exp(-1*((np.sum((pixelWindow - q_window)**2))/Nw))

        # Calculating Ip
        Ip_Numerator = Ip_Numerator + (w*Iq)
        Z = Z + w

    return Ip_Numerator/Z
     

class NLMeans():
  """
  Non Local Means, donot change the solve function. You may add any other class 
  functions or other functions in the colab file. but refrain for function/class
  definitions already given. These will be used to grade later on.
  """
  def example(self,img,**kwargs):
    denoised_image = cv2.fastNlMeansDenoising(img,**kwargs)
    return denoised_image

  def solve(self,img,h=30,small_window=7,big_window=21):
    """
    Solve function to perform nlmeans filtering.

    :param img: noisy image
    :param h: sigma h (as mentioned in the paper)
    :param small_window: size of small window
    :param big_window: size of big window
    :rtype: uint8 (w,h)
    :return: solved image
    """

    # Padding the original image with reflect mode
    padImg = np.pad(img,big_window//2,mode='reflect')

    return self.NLM(padImg,img,h,small_window,big_window)

  @staticmethod
  @jit(nopython = True, cache = True)
  def NLM(padImg, img, h, small_window, big_window):
    # Calculating neighborhood window
    Nw = (h**2)*(small_window**2)

    # Getting dimensions of the image
    h,w = img.shape

    # Initializing the result
    result = np.zeros(img.shape)

    # Finding width of the neighbor window and padded image from the center pixel
    bigWidth = big_window//2
    smallWidth = small_window//2

    # Preprocessing the neighbors of each pixel
    neighbors = findAllNeighbors(padImg, small_window, big_window, h, w) 

        # NL Means algorithm
    for i in range(bigWidth, bigWidth + h):
        for j in range(bigWidth, bigWidth + w):
            # (small_window x small_window) array for pixel p
            pixelWindow = neighbors[i,j]

            # (big_window x big_window) pixel neighborhhod array for pixel p
            neighborWindow = neighbors[(i - bigWidth):(i + bigWidth + 1) , (j - bigWidth):(j + bigWidth + 1)]

            # Calculating Ip using pixelWindow and neighborWindow
            Ip = evaluateNorm(pixelWindow, neighborWindow, Nw)

            # Cliping the pixel values to stay between 0-255 
            result[i - bigWidth, j - bigWidth] = max(min(255, Ip), 0)

    return result
  

