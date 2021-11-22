from setuptools import setup
setup(
    name='sindy_helper',
    version='0.0.1',
    entry_points={
        'console_scripts': [
            'sindy_helper=sindy_helper:run'
        ]
    }
)