import json
import numpy as np
from matplotlib import pyplot as plt

if __name__ == "__main__":
    with open("/Users/paulkreymborg/Downloads/nov_orientation/JoinedJsonSnakes/params_rt0.010_stretchfac0.1/joined_sectioned_auto_contrast_MTsAndBeads_40x_2umStep_20s_image_T0001_DA_FI_TR_Cy5_Cy7.json", "r") as f:
        contents = json.load(f)
    snakes = contents["snakes"]
    fg = []
    bg = []
    diff = []
    for snake in snakes:
        for pt in snake:
            fg.append(pt["fg"])
            bg.append(pt["bg"])
            diff.append(pt["fg"] - pt["bg"])
    fig = plt.figure()
    fig.add_subplot(311)
    plt.hist(fg, bins=np.linspace(0,65535,100))
    fig.add_subplot(312)
    plt.hist(bg, bins=np.linspace(0,65535,100))
    fig.add_subplot(313)
    plt.hist(diff, bins=np.linspace(-20000,65535,100))
    plt.show()
