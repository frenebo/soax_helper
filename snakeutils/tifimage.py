import numpy as np
import tifffile

# numpy arr should have (height,width,depth)
def save_3d_tif(fp,numpy_arr):
    # print("3D tif orig shape: {}".format(numpy_arr.shape))
    # tif takes (depth,height,width)
    numpy_arr = np.swapaxes(numpy_arr,2,1)
    numpy_arr = np.swapaxes(numpy_arr,1,0)
    # print("3D tif save shape: {}".format(numpy_arr.shape))

    tifffile.imsave(fp,numpy_arr)

def tif_img_3d_to_arr(pil_img):
    arr = np.zeros((pil_img.height,pil_img.width,pil_img.n_frames),dtype=np.array(pil_img).dtype)
    for frame_idx in range(pil_img.n_frames):
        pil_img.seek(frame_idx)
        arr[:,:,frame_idx] = np.array(pil_img)

    return arr