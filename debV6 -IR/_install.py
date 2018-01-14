#!/usr/bin/env python3.6

# Did this to install the packages I need from pip

import pip


packages = {
    'nltk',
    'beautifulsoup4',
}

for package in packages:
    print(f'$ python3.6 -m pip install -U {package}')
    pip.main(['install', '-U', package])
    print()


# What is this?! OWO
try:
    import nltk
    nltk.download('wordnet')
except ImportError:
    import traceback
    print('Your stuff is broken.')
    traceback.print_exc()
