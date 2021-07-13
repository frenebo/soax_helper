import numpy as np
import tifffile

# numpy arr should have (height,width,depth)
def save_3d_tif(fp,numpy_arr):
    print("3D tif orig shape: {}".format(numpy_arr.shape))
    # tif takes (depth,height,width)
    np.swapaxes(numpy_arr,2,1)
    np.swapaxes(numpy_arr,1,0)
    print("3D tif save shape: {}".format(numpy_arr.shape))

    tifffile.imsave(fp,numpy_arr)