
def create_params(
    intensity_scaling=0.0, # Should be equal to one to skip auto intensity scaling
    gaussian_std=0,
    ridge_threshold=0.01,
    maximum_foreground=65535,
    minimum_foreground=10,
    init_z=True,
    snake_point_spacing=5,
    min_snake_length=20,
    maximum_iterations=10000,
    change_threshold=0.1,
    check_period=100,
    alpha=0.01,
    beta=0.1,
    gamma=2,
    external_factor=1,
    stretch_factor=0.2,
    number_of_background_radial_sectors=8,
    background_z_xy_ratio=1,
    radial_near=4,
    radial_far=8,
    delta=4,
    overlap_threshold=1,
    grouping_distance_threshold=4,
    grouping_delta=8,
    minimum_angle_for_soac_linking=2.1,
    damp_z=False,
    ):
    params = """intensity-scaling	{intensity_scaling}
gaussian-std	{gaussian_std}
ridge-threshold	{ridge_threshold}
maximum-foreground	{maximum_foreground}
minimum-foreground	{minimum_foreground}
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
radial-near	{radial_near}
radial-far	{radial_far}
delta	{delta}
overlap-threshold	{overlap_threshold}
grouping-distance-threshold	{grouping_distance_threshold}
grouping-delta	{grouping_delta}
minimum-angle-for-soac-linking	{minimum_angle_for_soac_linking}
damp-z	{damp_z}""".format(
        minimum_foreground=minimum_foreground,
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
        radial_near=radial_near,
        radial_far=radial_far,
        delta=delta,
        overlap_threshold=overlap_threshold,
        grouping_distance_threshold=grouping_distance_threshold,
        grouping_delta=grouping_delta,
        minimum_angle_for_soac_linking=minimum_angle_for_soac_linking,
        damp_z=("true" if damp_z else "false"),
        maximum_foreground=maximum_foreground,
        )
    return params