from setuptools import setup

setup(
    name='plot_service',
    packages=['plot_service'],
    include_package_data=True,
    install_requires=[
        'flask',
        'numpy',
        'wtforms',
        'requests',
        'Pillow',
        'terrautils'
    ],
    dependency_links=[
        'git+https://github.com/terraref/terrautils@standard_sensor_path#egg=terrautils-1.0.0'
    ],
)
