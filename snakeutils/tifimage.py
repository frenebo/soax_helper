import numpy as np
import tifffile

# numpy arr should have (height,width,depth)
def save_3d_tif(fp,numpy_arr):
    # tif takes (depth,height,width)
    np.swapaxes(numpy_arr,2,1)
    np.swapaxes(numpy_arr,1,0)

    tifffile.imsave(fp,numpy_arr)