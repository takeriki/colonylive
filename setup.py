
from setuptools import setup, find_packages
setup(
    name='colonylive',
    version='1.0',
    packages = find_packages(),
    #install_requires=['numpy','scipy','rpy2','web.py'],
    scripts=[
            'clive/scripts/colonylive',
            'clive/scripts/colonylive-setup',
            'clive/scripts/clive_scan',
            'clive/scripts/clive_web',
            'clive/scripts/clive_analysis',
            ],

    extras_require = {
        'R': ["rpy2>=2.2.2"]
    },

    author = "Rikiya Takeuchi",
    author_email = "takeriki0502@gmail.com",
    description = "package for measurement and analysis of colony growth kinetics",
    license = "GNU GPLv3",
    keywords = "colony growth kintetics",
    homepage = "http://ecoli.naist.jp/colonylive/",

    platforms = "Python >= 2.7 on GNU/Linux"
    )

