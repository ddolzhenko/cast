from setuptools import setup, find_packages

ver = "0.1"

setup(

    name         = 'cast',
    version      = ver,

    description  = 'Ordering SW development process. Cast as a Model',
    keywords     = ['requirements', 'architecture'],

    author       = 'Dmitri Dolzhenko',
    author_email = 'd.dolzhenko@gmail.com',

    entry_points = {
        'console_scripts': [
            'cast = cast.console:main',
        ],
    },
    packages     = find_packages(),
    # test_suite   = 'cast.get_tests',

    url          = 'https://github.com/ddolzhenko/cast',
    download_url = 'https://github.com/ddolzhenko/cast/archive/v{}.tar.gz'.format(ver),

    classifiers  = [],
    install_requires = [
        "dirutil==0.4",
        "jinja2",
        "pyyaml"
    ],
)

