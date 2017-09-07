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
        'terrautils',
		'pyclowder'
    ],
    dependency_links=[
        'git+https://github.com/terraref/terrautils#egg=terrautils-1.0.0',
		'https://opensource.ncsa.illinois.edu/bitbucket/projects/CATS/repos/pyclowder2'
    ],
)
