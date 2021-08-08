
def create_params(
    alpha=0.01,
    beta=0.1,
    gamma=2,
    min_foreground=10,
    ridge_threshold=0.01,
    min_snake_length=20,
    gaussian_std=0,
    snake_point_spacing=5,
    external_factor=1):
    params = """intensity-scaling	0
gaussian-std	{gaussian_std}
ridge-threshold	{ridge_threshold}
maximum-foreground	65535
minimum-foreground	{min_foreground}
init-z	true
snake-point-spacing	{snake_point_spacing}
minimum-snake-length	{min_snake_length}
maximum-iterations	10000
change-threshold	0.1
check-period	100
alpha	{alpha}
beta	{beta}
gamma	{gamma}
external-factor	{external_factor}
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
        ridge_threshold=ridge_threshold,
        min_snake_length=min_snake_length,
        gaussian_std=gaussian_std,
        snake_point_spacing=snake_point_spacing,
        external_factor=external_factor,
        )
    return params