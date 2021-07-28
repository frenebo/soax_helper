
def create_params(alpha,beta,gamma,min_foreground,ridge_threshold):
    params = """intensity-scaling	0
gaussian-std	0
ridge-threshold	{ridge_threshold}
maximum-foreground	65535
minimum-foreground	{min_foreground}
init-z	true
snake-point-spacing	5
minimum-snake-length	20
maximum-iterations	10000
change-threshold	0.1
check-period	100
alpha	{alpha}
beta	{beta}
gamma	{gamma}
external-factor	1
stretch-factor	0.2
number-of-background-radial-sectors	8
background-z-xy-ratio	2.88
radial-near	4
radial-far	8
delta	4
overlap-threshold	1
grouping-distance-threshold	4
grouping-delta	8
minimum-angle-for-soac-linking	2.1
damp-z	false""".format(
        min_foreground=min_foreground,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        ridge_threshold=ridge_threshold,
        )
    return params