import numpy as np
def thicken(arr):
    new_arr = np.zeros(arr.shape, dtype=arr.dtype)
    # print(arr[:,0:-1])
    new_arr += arr
    # Left
    new_arr[:,:-1] += arr[:,1:]
    # Right
    new_arr[:,1:] += arr[:,:-1]
    # Up
    new_arr[:-1,:] += arr[1:,:]
    # Down
    new_arr[1:,:] += arr[:-1,:]
    # print(new_arr)
    # new_arr[:,0:-1] =
    # a[:,0:-1] a[:,1:]
    # left_shift = a[:,1:]
    # right_shift = a
    new_arr[new_arr > 1] = 1
    return new_arr

if __name__ == "__main__":
    a = np.array([
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
    ])
    for i in range(3):
        a = thicken(a)
    print(a)