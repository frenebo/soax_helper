#!python

import numpy as np
from scipy.integrate import odeint, cumtrapz
from scipy.fftpack import diff as psdiff
import matplotlib.pyplot as plt
import scipy.optimize as opt
import csv
from scipy.signal import fftconvolve
from PIL import Image
import math

from scipy import signal
from skimage import morphology

from snakeutils.snakejson import load_json_snakes




# startLoc = []
# nPts = []

# with open('data.txt', 'r') as file:
#      contents = file.read()

# for i in range(0, nSnake):
#     startLoc.append(contents.find('\n'+str(i)))

# for i in range(1, nSnake):
#     nPts.append(int(contents[startLoc[i]-66:startLoc[i]-63]))

# nPts.append(int(contents[-64:-60]))





# #Load all the snakes
data_path = "/Users/paulkreymborg/Downloads/nov_orientation/JoinedJsonSnakes/params_rt0.010_stretchfac0.1/joined_sectioned_auto_contrast_MTsAndBeads_40x_2umStep_20s_image_T0001_DA_FI_TR_Cy5_Cy7.json"

snakes, metadata = load_json_snakes(data_path)

X = []
Y = []
Z = []

for snake in snakes:
    xdata = []
    ydata = []
    zdata = []
    for pt in snake:
        x,y,z = pt["pos"]
        xdata.append(x)
        ydata.append(y)
        zdata.append(z)
    X.append(xdata)
    Y.append(ydata)
    Z.append(zdata)
    break


# Taking derivatives
from scipy.interpolate import splrep, splder, splev
import scipy.optimize as optimize
from scipy.interpolate import UnivariateSpline

def reslice(x, y, z):
    l=np.zeros_like(x)
    l[:-1] = cumtrapz(np.sqrt(np.diff(np.asarray(z))**2+np.diff(np.asarray(y))**2+np.diff(np.asarray(x))**2), initial=0)
    l[-1] = np.sum(np.sqrt(np.diff(np.asarray(z))**2+np.diff(np.asarray(y))**2+np.diff(np.asarray(x))**2))
    s = np.linspace(0, l[-1], len(x))
    spl_x = UnivariateSpline(l, x)
    spl_x.set_smoothing_factor(0)
    spl_y = UnivariateSpline(l, y)
    spl_y.set_smoothing_factor(0)
    spl_z = UnivariateSpline(l, z)
    spl_z.set_smoothing_factor(0)
    even_x = spl_x(s)
    even_y = spl_y(s)
    even_z = spl_z(s)
    ds = s[1]
    return even_x, even_y, even_z, ds


def dogker1(size, sigma):
    x = np.linspace(-size, size, 2*size+1)
    k = -x*np.exp((-x**2)/(2*sigma^2))/np.sqrt(2*sigma**2)
    k = k/np.abs(np.sum(k))
    return k

def dogker2(size, sigma):
    x = np.linspace(-size, size, 2*size+1)
    k = x**2*np.exp((-x**2)/(2*sigma^2))/(2*sigma**2)-np.exp((-x**2)/(2*sigma^2))/np.sqrt(2*sigma**2)
    k = k/np.abs(np.sum(k))
    return k

# def Dif(y, dx, order):
#     if order == 1:
#         der =
#     elif order == 2:
#         raise Exception("Unimplemented")
#     return der

# def Dif(y, dx, order):
#     if order==1:
#         ker = dogker1(5, 3)
#         print(ker)
#         der = fftconvolve(y, ker, mode='same')/dx
#     elif order==2:
#         ker = dogker2(5, 3)
#         der = fftconvolve(y, ker, mode='same')/dx**2
#     return der

def orientation(x, y, z, ds):
    pts = np.zeros((3, len(x)))
    pts[0,:] =x
    pts[1,:] =y
    pts[2,:] =z

    # print("PTS: {}".format(pts.s
    # pts = np.array((x,y,z))
    segment_diffs = pts[:,1:] - pts[:,0:-1]
    # print("Segment diffs {}: ".format(segment_diffs.shape))
    # print(segment_diffs)
    start_pt_orientation = segment_diffs[:,0]
    end_pt_orientation = segment_diffs[:,-1]
    between_pt_diffs = (segment_diffs[:,:-1] + segment_diffs[:,1:]) / 2
    # print("Between pt diffs {}".format(between_pt_diffs.shape))
    orient = np.zeros((3, len(x)))
    orient[:,0] = start_pt_orientation
    orient[:,-1] = end_pt_orientation
    orient[:,1:-1] = between_pt_diffs

    # between_orient = diffs
    # orient = np.zeros((3, len(x)));
    # orient[0, :] = Dif(x, dx, 1)
    # orient[1, :] = Dif(y, dx, 1)
    # orient[2, :] = Dif(z, dx, 1)

    # print("Orientation:")
    # print(orient)
    orient = orient/np.sqrt(orient[0, :]**2 + orient[1, :]**2+ orient[2, :]**2)
    # print("Normalized:")
    # print(orient)

    return orient


def Qtensor(x, y, z, ds):
    nx, ny, nz = orientation(x, y, z, ds)
    Q = np.zeros((3, 3, len(x)))
    Q[0, 0, :] = nx*nx
    Q[1, 1, :] = ny*ny
    Q[2, 2, :] = nz*nz
    Q[0, 1, :] = nx*ny
    Q[0, 2, :] = nx*nz
    Q[1, 2, :] = ny*nz
    Q[1, 0, :] = Q[0, 1, :]
    Q[2, 0, :] = Q[0, 2, :]
    Q[2, 1, :] = Q[1, 2, :]
    return Q

# def curvature(x, y, z, dx):
#     dx1 = Dif(x, dx, 1)
#     dx2 = Dif(x, dx, 2)
#     dy1 = Dif(y, dx, 1)
#     dy2 = Dif(y, dx, 2)
#     dz1 = Dif(z, dx, 1)
#     dz2 = Dif(z, dx, 2)

#     k1 = (dy1*dz2 - dz1*dy2)**2
#     k2 = (dz1*dx2 - dx1*dz2)**2
#     k3 = (dx1*dy2 - dy1*dx2)**2
#     r = np.sqrt(dx1**2 + dy1**2 + dz1**2)
#     kappa = np.sqrt(k1+k2+k3)/(r**3)
#     return kappa

def importtif(tif_path):
    dataset = Image.open(tif_path)
    h,w = np.shape(dataset)
    tiffarray = np.zeros((h,w,dataset.n_frames))
    for i in range(dataset.n_frames):
        dataset.seek(i)
        tiffarray[:,:,i] = np.array(dataset)
    return tiffarray







# choose snake number
sn= 0

#Show the snake that we are interested in
# fig = plt.figure(figsize=(8,8))
# ax = plt.axes(projection='3d')

# ax.scatter3D(np.asarray(X[sn]), np.asarray(Y[sn]), np.asarray(Z[sn]));


#First we resample the snake evenly along its countour
#and check whether it is the same as the original

even_x, even_y, even_z, ds = reslice(X[sn], Y[sn], Z[sn])
print("Even x, y, z:")
print(even_x)
print(even_y)
print(even_z)

stdev = np.std(np.sqrt(np.diff(even_x)**2 + np.diff(even_y)**2+ np.diff(even_z)**2))

# fig = plt.figure(figsize=(8,8))
# ax = plt.axes(projection='3d')

# ax.scatter3D(np.asarray(X[sn]), np.asarray(Y[sn]), np.asarray(Z[sn]), color='b');
# ax.scatter3D(even_x, even_y, even_z, color='r');

# ax.legend(('Original snake', 'Resampled snake'));
# print('Standard deviation of ds is '+str(int(stdev*10**4)/10**4));

#Then, we check that we are finding the orientation properly

nx, ny, nz = orientation(even_x, even_y, even_z, ds)

fig = plt.figure(figsize=(8,8))
ax = plt.axes(projection='3d')

# for i in range(len(even_x)):
#     x_vals = [even_x[i], even_x[i] + nx[i]]
#     y_vals = [even_y[i], even_y[i] + ny[i]]
#     z_vals = [even_z[i], even_z[i] + nz[i]]
#     # pts = [
#     #     [even_x[i], even_y[i], even_z[i]],
#     #     [even_x[i] + nx[i], even_y[i] + ny[i], even_z[i] + nz[i]],
#     # ]
#     plt.plot(x_vals, y_vals, z_vals, 'r')
plt.plot(even_x, even_y, even_z, 'r.')
ax.quiver(even_x, even_y,even_z, nx, ny, nz)
# print(nx)
# print(ny)
# print(nz)


plt.show()

#Next, we check the Q tensor (just be sure it runs with no errors)

Q = Qtensor(even_x, even_y, even_z, ds)
Q[:, :, 1]


# # #Finally, we check that the curvature is okay

# k = curvature(even_x, even_y, even_z, ds)

# #Color by k

# fig = plt.figure()
# ax = plt.axes(projection='3d')

# ax.scatter3D(np.asarray(X[sn]), np.asarray(Y[sn]), np.asarray(Z[sn]), c = k);




# tif_path = r'/Users/paulkreymborg/Downloads/nov_orientation/AutoContrastedTIFFs/auto_contrast_MTsAndBeads_40x_2umStep_20s_image_T0001_DA_FI_TR_Cy5_Cy7.tif'
# tifstack = importtif(tif_path)


# density=np.zeros_like(tifstack)

# xx = []
# yy = []
# zz = []

# for sn in range(0, len(X)): # snake number
#     even_x, even_y, even_z, ds = reslice(X[sn], Y[sn], Z[sn])
#     xx = xx + list(even_x)
#     yy = yy + list(even_y)
#     zz = zz + list(even_z)
#     for k in range(0, len(even_x)):
#         density[math.floor(Y[sn][k]) - 1, math.floor(X[sn][k]) - 1, math.floor(Z[sn][k]) - 1]=1

# fig = plt.figure(figsize=(8,8))
# ax = plt.axes(projection='3d')

# print(len(xx))
# # ax.scatter3D(xx, yy, zz);






#Run the analysis assuming SINDy works for thin snakes
out_file = r'/Users/paulkreymborg/Downloads/nov_orientation/snakeData.dat'

xdata = []
ydata = []
zdata = []
Qxx = []
Qyy = []
Qzz = []
Qxy = []
Qxz = []
Qyz = []

for sn in range(0, len(X)): # snake number
    even_x, even_y, even_z, ds = reslice(X[sn], Y[sn], Z[sn])
    xdata = xdata + list(np.round(even_x))
    ydata = ydata + list(np.round(even_y))
    zdata = zdata + list(np.round(even_z))
    Q = Qtensor(even_x, even_y, even_z, ds)
    Qxx = Qxx + list(Q[0, 0, :])
    Qyy = Qyy + list(Q[1, 1, :])
    Qzz = Qzz + list(Q[2, 2, :])
    Qxy = Qxy + list(Q[0, 1, :])
    Qxz = Qxz + list(Q[0, 2, :])
    Qyz = Qyz + list(Q[1, 2, :])

CorArr = np.asarray(list(zip(xdata, ydata, zdata)))
inds = np.where(CorArr==np.unique(CorArr, axis=1))[0]

OutputData = np.zeros((len(inds), 9))

OutputData[:, 0] = np.asarray(xdata)[inds]
OutputData[:, 1] = np.asarray(ydata)[inds]
OutputData[:, 2] = np.asarray(zdata)[inds]
OutputData[:, 3] = np.asarray(Qxx)[inds]
OutputData[:, 4] = np.asarray(Qyy)[inds]
OutputData[:, 5] = np.asarray(Qzz)[inds]
OutputData[:, 6] = np.asarray(Qxy)[inds]
OutputData[:, 7] = np.asarray(Qxz)[inds]
OutputData[:, 8] = np.asarray(Qyz)[inds]

np.savetxt(out_file, OutputData, fmt=['%d','%d','%d','%f','%f','%f','%f','%f','%f'])

exit()



#Run the analysis assuming SINDy requires an intensity field

out_file = r'/Users/paulkreymborg/Downloads/nov_orientation/snakeDataWithI.dat'

tif_path = r'/Users/paulkreymborg/Downloads/nov_orientation/AutoContrastedTIFFs/auto_contrast_MTsAndBeads_40x_2umStep_20s_image_T0001_DA_FI_TR_Cy5_Cy7.tif'

xdata = []
ydata = []
zdata = []
I = []
Qxx = []
Qyy = []
Qzz = []
Qxy = []
Qxz = []
Qyz = []

for sn in range(0, len(X)): # snake number
    even_x, even_y, even_z, ds = reslice(X[sn], Y[sn], Z[sn])
    xdata = xdata + list(np.round(even_x))
    ydata = ydata + list(np.round(even_y))
    zdata = zdata + list(np.round(even_z))
    for ii in range(0, len(X[sn])):
        I.append(tifstack[int(Y[sn][ii]),int(X[sn][ii]),int(Z[sn][ii])])
    Q = Qtensor(even_x, even_y, even_z, ds)
    Qxx = Qxx + list(Q[0, 0, :])
    Qyy = Qyy + list(Q[1, 1, :])
    Qzz = Qzz + list(Q[2, 2, :])
    Qxy = Qxy + list(Q[0, 1, :])
    Qxz = Qxz + list(Q[0, 2, :])
    Qyz = Qyz + list(Q[1, 2, :])

CorArr = np.asarray(list(zip(xdata, ydata, zdata)))
inds = np.where(CorArr==np.unique(CorArr, axis=1))[0]

OutputData = np.zeros((len(inds), 10))

OutputData[:, 0] = np.asarray(xdata)[inds]
OutputData[:, 1] = np.asarray(ydata)[inds]
OutputData[:, 2] = np.asarray(zdata)[inds]
OutputData[:, 3] = np.asarray(I)[inds]
OutputData[:, 4] = np.asarray(Qxx)[inds]
OutputData[:, 5] = np.asarray(Qyy)[inds]
OutputData[:, 6] = np.asarray(Qzz)[inds]
OutputData[:, 7] = np.asarray(Qxy)[inds]
OutputData[:, 8] = np.asarray(Qxz)[inds]
OutputData[:, 9] = np.asarray(Qyz)[inds]

np.savetxt(out_file, OutputData, fmt=['%d','%d','%d','%f','%f','%f','%f','%f','%f','%f'])





#Snake dilation

maxWidth=20

tif_path = r'/Users/paulkreymborg/Downloads/nov_orientation/AutoContrastedTIFFs/auto_contrast_MTsAndBeads_40x_2umStep_20s_image_T0001_DA_FI_TR_Cy5_Cy7.tif'
tifstack = importtif(tif_path)
density = np.zeros_like(tifstack)
temp = np.zeros_like(tifstack)

struct = np.ones((maxWidth, maxWidth, maxWidth))

for sn in range(0, len(X)): # snake number
    for k in range(0, len(X[sn])):
        temp[int(Y[sn][k]), int(X[sn][k]), int(Z[sn][k])] = 1

b = 1*morphology.ball(radius=10)
dilated = signal.fftconvolve(temp, b, mode='same')>0.1

stk = dilated*(tifstack - 2*np.mean(tifstack))
stk[stk<0]=0





#Find the tangents to the curve

def tans1(nx, ny, nz):
    tangs = np.zeros((3, len(nx)));

    tangs[0, :] = ny
    tangs[1, :] = -nx
    tangs[2, :] = 0

    tangs=tangs/np.sqrt(tangs[0, :]**2+tangs[1, :]**2+tangs[2, :]**2)

    return tangs

def tans2(nx, ny, nz, tx, ty, tz):
    tangs = np.zeros((3, len(nx)));

    tangs[0, :] = (ny*tz - nz*ty)
    tangs[1, :] = (nz*tx - nx*tz)
    tangs[2, :] = (nx*ty - ny*tx)

    tangs=tangs/np.sqrt(tangs[0, :]**2+tangs[1, :]**2+tangs[2, :]**2)

    return tangs

nx, ny, nz = orientation(even_x, even_y, even_z, ds)
tx1, ty1, tz1 = tans1(even_x, even_y, even_z)
tx2, ty2, tz2 = tans2(nx, ny, nz, tx1, ty1, tz1)

fig = plt.figure(figsize=(8,8))
ax = plt.axes(projection='3d')

plt.plot(even_x, even_y, even_z, 'r.')
ax.quiver(even_x, even_y,even_z, tx1, ty1, tz1)
ax.quiver(even_x, even_y,even_z, tx2, ty2, tz2)





