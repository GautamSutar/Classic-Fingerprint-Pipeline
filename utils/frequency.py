import numpy as np
import math
import scipy.ndimage


def frequest(im, orientim, kernel_size, minWaveLength, maxWaveLength):
    rows, cols = np.shape(im)
    
    cosorient = np.cos(2*orientim)
    sinorient = np.sin(2*orientim)
    block_orient = math.atan2(sinorient,cosorient)/2
    
    rotim = scipy.ndimage.rotate(im,block_orient/np.pi*180 + 90,axes=(1,0),reshape = False,order = 3,mode = 'nearest')

    cropsze = int(np.fix(rows/np.sqrt(2)))
    offset = int(np.fix((rows-cropsze)/2))
    rotim = rotim[offset:offset+cropsze][:,offset:offset+cropsze]

    ridge_sum = np.sum(rotim, axis = 0)
    dilation = scipy.ndimage.grey_dilation(ridge_sum, kernel_size, structure=np.ones(kernel_size))
    ridge_noise = np.abs(dilation - ridge_sum); peak_thresh = 2;
    maxpts = (ridge_noise < peak_thresh) & (ridge_sum > np.mean(ridge_sum))
    maxind = np.where(maxpts)
    _, no_of_peaks = np.shape(maxind)
    
    if(no_of_peaks<2):
        freq_block = np.zeros(im.shape)
    else:
        waveLength = (maxind[0][-1] - maxind[0][0])/(no_of_peaks - 1)
        if waveLength>=minWaveLength and waveLength<=maxWaveLength:
            freq_block = 1/np.double(waveLength) * np.ones(im.shape)
        else:
            freq_block = np.zeros(im.shape)
    return(freq_block)


def ridge_freq(im, mask, orient, block_size, kernel_size, minWaveLength, maxWaveLength):
    rows, cols = im.shape
    freq = np.zeros((rows, cols))

    for r in range(0, rows - block_size, block_size):
        for c in range(0, cols - block_size, block_size):
            image_block = im[r:r + block_size, c:c + block_size]
            angle_block = orient[r // block_size, c // block_size]
            
            if np.sum(mask[r:r + block_size, c:c + block_size]) > 0:
                freq_block = frequest(image_block, angle_block, kernel_size, minWaveLength, maxWaveLength)
                freq[r:r + block_size, c:c + block_size] = freq_block

    return freq