import os
import io
from setuptools import setup

dir = os.path.dirname(__file__)

# long description from README file
with open('README.md', encoding='utf-8') as f:
    DESCRIPTION = f.read()

REQUIRED = open('requirements.txt').read()

setup(
    name='simplifiedpytrends',
    version='1.0.4',
    description='Simplified Pseudo API for Google Trends',
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/Drakkar-Software/pytrends',
    author=['John Hogue', 'Burton DeWilde', 'DrakkarSoftware'],
    author_email='drakkar.software@protonmail.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: MIT License",
        ],
    install_requires=REQUIRED,
    keywords='google trends api search',
    packages=['simplifiedpytrends'],
)
