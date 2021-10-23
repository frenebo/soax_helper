import numpy as np
import cv2
from PIL import Image

import os

from snakeutils.logger import PrintLogger
from snakeutils.files import find_files_or_folders_at_depth, pil_img_3d_to_np_arr

def loadData(file_path):
    dataset = Image.open(file_path)
    h,w = np.shape(dataset)
    tiffarray = np.zeros((h,w,dataset.n_frames))
    for i in range(dataset.n_frames):
        dataset.seek(i)
        tiffarray[:,:,i] = np.array(dataset)
    return tiffarray.astype(np.double)

def xcorr3fft(image1,image2):

    F = np.fft.fftn(image1);
    Fc = np.conj(np.fft.fftn(image2));

    R = F.*Fc; # Phase correlation, Compute fft of image1 and conjugate fft of image2, elementwise multiply and normalise.
    c = np.fft.ifftn(R); # Inverse fft of Phase correlation gives cross correlation map.
    [~,i] = np.max(c);

    [I,J,K] = np.unravel_index(np.shape(c),i);


    if abs(I-1)<abs(np.shape(image1)[0]-I+1):
        shiftx = -I+1;
    else:
        shiftx =  np.shape(image1)[0]-I+1;

    if abs(J-1)<abs(np.shape(image1)[1]-J+1):
        shifty = -J+1;
    else:
        shifty = np.shape(image1)[1]-J+1;

    if abs(K-1)<abs(np.shape(image1)[2]-K+1):
        shiftz = -K+1;
    else:
        shiftz = np.shape(image1)[2]-K+1;

    return shiftx,shifty,shiftz

def GetPIV3d(im1,im2,X1,Y1,Z1,edge_length):
    si = np.shape(im1);
    nb = np.ceil(si/edge_length); #Floor?
    counter = 0;
    shiftx = np.zeros((1,nb[1]*nb[2]*nb[3]));
    shifty = np.zeros_like(shiftx);
    shiftz = np.zeros_like(shiftx);
    x = np.zeros_like(shiftx);
    y = np.zeros_like(shiftx);
    z = np.zeros_like(shiftx);
    window = 15;

    for i in range(0, nb[1]):
        for j in range(0, nb[2]):
            for k in range(0, nb[3]):

                #cut a cube out of the image
                temp1 = im1[
                        max(0,((i-1)*edge_length-window)):min((i+1)*edge_length+window,si[0]),
                        max(0,(j-1)*edge_length-window)):min((j+1)*edge_length+window,si[1]),
                        max(0,(k-1)*edge_length-window)):min((k+1)*edge_length+window,si[2]),
                        ]

                temp2 = im2[
                        max(0,((i-1)*edge_length-window)):min((i+1)*edge_length+window,si[0]),
                        max(0,(j-1)*edge_length-window):min((j+1)*edge_length+window,si[1]),
                        max(0,(k-1)*edge_length-window):min((k+1)*edge_length+window,si[2]),
                        ]

                shiftx[counter],shifty[counter],shiftz[counter] = xcorr3fft(temp1,temp2);
                x[counter] = (i-0.5)*edge_length;
                y[counter] = (j-0.5)*edge_length;
                z[counter] = (k-0.5)*edge_length;
                counter = counter+1;

    # Put the flow field on a grid
    VX  = griddata(x,y,z,shiftx,X1,Y1,Z1);
    VY  = griddata(x,y,z,shifty,X1,Y1,Z1);
    VZ  = griddata(x,y,z,shiftz,X1,Y1,Z1);
    return VX,VY,VZ

def tube_piv(
    source_tiff_dir,
    target_velocities_dir,
    edge_length=5,
    logger=PrintLogger,
    ):
    source_dir_info = find_files_or_folders_at_depth(source_tiff_dir, 0, file_extensions=[".tif", ".tiff"])


    for time_idx in len(source_dir_info - 1):
        containing_folder1, tif_name1 = source_dir_info[time_idx]
        im1_path = os.path.join(containing_folder1, tif_name1)
        containing_folder2, tif_name2 = source_dir_info[time_idx + 1]
        im2_path = os.path.join(containing_folder2, tif_name2)
        im1 = loadData(im1_path)
        im2 = loadData(im2_path)

        L1, L2, L3 = np.shape(im1)

        # define the grid on which to compute the flow field
        [X1,Y1,Z1] = np.meshgrid(np.linspace(edge_length/2, L1-edge_length/2, int(L1/edge_length-1)),
                                np.linspace(edge_length/2, L2-edge_length/2, int(L3/edge_length-1)),
                                np.linspace(edge_length/2, L2-edge_length/2, int(L3/edge_length-1)))

        shiftx, shifty, shiftz = GetPIV3d(im1, im2, X1, Y1, Z1, edge_length)

        # im1 = pil_img_3d_to_np_arr(im1_path)

    # velfolder='\PIV'; #Open folder

    # if (isfolder(basepath + velfolder)!=1):
    #     mkdir(basepath + velfolder)

    NTimes = 20;
    timestart = 10;
    isf = 1;          # image scaling factor.
    step = 1;         # step in timeframes.
    smooth = False
    sigma = .8;       # standard deviation of gaussian kernel
    im1 = loadData(basepath + '\TP'+t+'_Ch0_Ill0_Ang0,90,180,270.tif');
    im1 = cv2.resize(im1, dsize=isf*np.shape(im1),
                    interpolation=cv2.INTER_CUBIC);
    stackSize = np.shape(im1)[2];
    slice_index = np.linspace(0, stackSize);
    temp_im = loadData(basepath + '\TP'+timestart+'_Ch0_Ill0_Ang0,90,180,270.tif');
    for sl in range(0, len(slice_index)):
        tempImSl = temp_im[slice_index[sl]]
        im1(:,:,sl) = cv2.resize(tempImSl, dsize=isf*np.shape(tempImSl),
                                interpolation=cv2.INTER_CUBIC);

    for time in range(timestart, timestart+NTimes):
        #read the images
        tp_1_name = basepath + '\TP'+time+'_Ch0_Ill0_Ang0,90,180,270.tif';
        tp_2_name = basepath + '\TP'+str(time+step)+'_Ch0_Ill0_Ang0,90,180,270.tif';

        #read Image stacks and down sample
        if time == 0:
            stackSize = len(imfinfo(tp_1_name));

        slice_index = np.linspace(0, stackSize, int(stackSize/isf));
        temp_im1 = loadData(tp_1_name);
        temp_im2 = loadData(tp_2_name);

        for sl in range(0,  len(slice_index)):
            tempSl1 = temp_im1[slice_index[sl]]
            im1[:,:,sl] = cv2.resize(tempSl1, dsize=isf*np.shape(tempSl1),
                                    interpolation=cv2.INTER_CUBIC);

            tempSl2 = temp_im2[slice_index[sl]]
            im2[:,:,sl] = cv2.resize(tempSl2, dsize=isf*np.shape(tempSl2),
                                    interpolation=cv2.INTER_CUBIC);

        #compute the piv flow field
        VY,VX,VZ = GetPIV3d(im1,im2,X1,Y1,Z1,edge_length);

        #smooth if desired
        if (smooth == 1):
            VX  = imgaussfilt3(VX, sigma);
            VY  = imgaussfilt3(VY, sigma);
            VZ  = imgaussfilt3(VZ, sigma);

        np.save(basepath + folder + '/VX_'+time+'.npy',VX);
        np.save(basepath + folder + '/VY_'+time+'.npy',VY);
        np.save(basepath + folder + '/VZ_'+time+'.npy',VZ);

