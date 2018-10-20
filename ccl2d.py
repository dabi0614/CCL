#!/usr/bin/env python

import cv2
import numpy as np

def ccl2d(data_in,thresh,verbose=False,graph=False):

    nlat = data_in.shape[0]
    nlon = data_in.shape[1]
    
    data = np.zeros(data_in.shape,dtype=np.uint8)
    mx = np.nanmax(data_in)
    if mx == 0:
        mx = 1;
    data[:,:] = 255*(data_in[:,:]/mx)
    d_lo = int(255*(thresh[0]/mx))
    d_hi = int(255*(thresh[1]/mx))

    if verbose:
        print('data-mnmx: ',np.nanmin(data_in),np.nanmax(data_in))
        print('type:  ',type(data))
        print('dtype: ',data.dtype)
        print('shape: ',data.shape)
        print('selection data mnmx: ',d_lo,d_hi)
        
    if False:
        cv2.imshow('data_in',data_in); cv2.waitKey(0); cv2.destroyAllWindows()

    ret, thresh = cv2.threshold(data, d_lo, d_hi, cv2.THRESH_BINARY)
#   ret, thresh = cv2.threshold(data, 7, 7.74, cv2.THRESH_BINARY_INV)

    if verbose:
        print ('thresh-ret: ',ret)
        print('type(thresh): ',type(thresh))
        print('type(thresh[0,0]): ',type(thresh[0,0]))
        print('thresh.dtype: ',thresh.dtype)
        print('thresh mnmx: ',np.nanmin(thresh),np.nanmax(thresh))
        print('thresh uniq: ',np.unique(thresh))
        print('thresh[0:3,0:3]: ',thresh[0:3,0:3])
        print('thresh[nlat-3:nlat-1,0:3]: ',thresh[nlat-3:nlat-1,0:3])
    if False:
        cv2.imshow('thresh',thresh); cv2.waitKey(0); cv2.destroyAllWindows()

    ret, markers = cv2.connectedComponents(thresh)
    
    if verbose:
        print ('markers-ret: ',ret)
        print('markers: ',np.amax(markers))

    markers_mx = np.amax(markers)
    if markers_mx == 0:
        markers_mx = 1
    data1 = markers.astype(np.float)/markers_mx

    if graph:
        cv2.imshow('markers',data1); cv2.waitKey(0); cv2.destroyAllWindows()

    if verbose:
        print('bot box: ',markers[   0:3,0:3])
        print('top box: ',markers[nlat-3:nlat-1,0:3])

    # Say the elements touching the poll are the same cell
    bot_unique = np.unique(markers[  0,:])
    if len(bot_unique)>1:
        bot_label  = bot_unique[1]
        for i in range(1,bot_unique.size):
            markers[np.where(markers == bot_unique[i])] = bot_label
    top_unique = np.unique(markers[  nlat-1,:])
    if len(top_unique)>1:    
        top_label  = top_unique[1]
        for i in range(1,top_unique.size):
            markers[np.where(markers == top_unique[i])] = top_label

    if verbose:
        print('bot box: ',markers[   0:3,0:3])
        print('top box: ',markers[nlat-3:nlat-1,0:3])

    # Periodic in longitude
    dateline_check_thresh_idx_0 = \
        np.where(
            (thresh[ :  ,0] == thresh[ :  ,nlon-1]) &
            (thresh[:,nlon-1] == 255)
        )[0]
    dateline_check_thresh_idx_p = \
        np.where(
            (thresh[1:  ,0] == thresh[ :-1,nlon-1]) &
            (thresh[:-1,nlon-1] == 255)
        )[0]
    dateline_check_thresh_idx_m = \
        np.where(
            (thresh[ :-1,0] == thresh[1:  ,nlon-1]) &
            (thresh[1:,nlon-1] == 255)
        )[0]

    # print 'dateline_check_thresh_idx_0: ',dateline_check_thresh_idx_0
    id_0 = []
    for i in dateline_check_thresh_idx_0:
        # print 'i: ',i
        id_0.append([markers[i,0],markers[i,nlon-1]])
    # print 'id_0: ',id_0
    
    id_p = []
    for i in dateline_check_thresh_idx_p:
        id_p.append([markers[i+1,0],markers[i,nlon-1]])
    # print('id_p: ',id_p)

    id_m = []
    for i in dateline_check_thresh_idx_m:
        id_m.append([markers[i,0],markers[i+1,nlon-1]])
    # print('id_m: ',id_m)

    id_all = id_0 + id_p + id_m
    id_all_fixed = []
    for i in id_all:
        if (min(i) != max(i)):
            id_all_fixed.append([min(i),max(i)])
        
    id_all_uniq = []
    for i in id_all_fixed:
        if (i not in id_all_uniq):
            id_all_uniq.append(i)
    for i in range(len(id_all_uniq)):
        r = id_all_uniq[i]
        for j in range(i+1,len(id_all_uniq)):
            s = id_all_uniq[j]
            if r[1] == s[0]:
                id_all_uniq[j][0]=r[0]

    if verbose:
        print "id_all:      ",id_all
        print "id_all_uniq: ",id_all_uniq
    if verbose:
        print '100: ',np.unique(markers)
    for i in id_all_uniq:
        if verbose:
            print 'i: ',i
        markers[np.where(markers == i[1])] = i[0]
    markers_unique=np.unique(markers)
    if verbose:
        print '110: ',markers_unique
    for i in range(len(markers_unique)):
        markers[np.where(markers == markers_unique[i])] = i
    markers_unique_1=np.unique(markers)
    if verbose:
        print '120: ',markers_unique_1

    data2 = np.zeros(markers.shape,dtype=np.uint8)
    markers_mx = np.amax(markers)
    if markers_mx == 0:
        markers_mx = 1
    data2[:,:] = 255*(markers.astype(np.float)/markers_mx)
    # data2 = cv2.applyColorMap(data2,cv2.COLORMAP_RAINBOW)

    if graph:
        cm = np.zeros((256,1,3),np.uint8)
        cm[:,0,0] = 255-np.arange(256)
        cm[:,0,1] = (np.arange(256)*(255-np.arange(256)))/255
        cm[:,0,2] = np.arange(256)
        cm[0,0,:] = 0
        data2 = cv2.applyColorMap(data2,cm)
        cv2.imshow('markers',data2)
        cv2.waitKey(0); cv2.destroyAllWindows()

    # print('type(cm): ',type(cv2.COLORMAP_RAINBOW))
    # print('cm:       ',cv2.COLORMAP_RAINBOW)

    return markers

if __name__ == '__main__':
    print 'ccl2d start'

    from Krige import DataField as df

    if True:
        obj = df.DataField(\
                           datafilename='MYD08_D3.A2015304.061.2018054061429.hdf'\
                           ,datafieldname='Atmospheric_Water_Vapor_Mean'\
                           ,srcdirname='/home/mrilee/data/NOGGIN/MODIS-61-MYD08_D3/'\
        )
        markers = ccl2d(obj.data,(7.25,7.74),graph=True)

    print 'ccl2d done'

