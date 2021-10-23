
def create_params(
    alpha=0.01,
    beta=0.1,
    gamma=2,
    min_foreground=10,
    ridge_threshold=0.01,
    min_snake_length=20,
    gaussian_std=0,
    snake_point_spacing=5,
    external_factor=1,
    intensity_scaling=0.0, # Should be equal to one to skip auto intensity scaling
    stretch_factor=0.2,
    init_z=True,
    maximum_iterations=10000,
    change_threshold=0.1,
    check_period=100,
    number_of_background_radial_sectors=8,
    background_z_xy_ratio=1,
    ):
    params = """intensity-scaling	{intensity_scaling}
gaussian-std	{gaussian_std}
ridge-threshold	{ridge_threshold}
maximum-foreground	65535
minimum-foreground	{min_foreground}
init-z	{init_z_str}
snake-point-spacing	{snake_point_spacing}
minimum-snake-length	{min_snake_length}
maximum-iterations	{maximum_iterations}
change-threshold	{change_threshold}
check-period	{check_period}
alpha	{alpha}
beta	{beta}
gamma	{gamma}
external-factor	{external_factor}
stretch-factor	{stretch_factor}
number-of-background-radial-sectors	{number_of_background_radial_sectors}
background-z-xy-ratio	{background_z_xy_ratio}
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
        min_snake_length=min_snake_length,
        gaussian_std=gaussian_std,
        snake_point_spacing=snake_point_spacing,
        external_factor=external_factor,
        intensity_scaling=intensity_scaling,
        stretch_factor=stretch_factor,
        init_z_str=("true" if init_z else "false"),
        maximum_iterations=maximum_iterations,
        change_threshold=change_threshold,
        check_period=check_period,
        number_of_background_radial_sectors=number_of_background_radial_sectors,
        background_z_xy_ratio=background_z_xy_ratio,
        )
    return params