from distutils.core import setup

setup(
    name='MaterialsDatabase',
    version='1.0.0',
    author='Thien Huong Vu',
    author_email='thv20@cam.ac.uk',
    license='MIT',
    url='https://github.com/lexievu/MaterialsDatabase',
    description='Package attempting to find chemical formulae and their corresponding magnetic properties',
    long_description=open('README.md').read(),
    long_description_content_type='Markdown',
    packages=['doc_processing', 'utility', 'webscraping'],
    install_requires=[
        'numpy', 'matplotlib', 'mat2vec', 'regex', 'nltk', 'tqdm', 'unidecode', 'monty',
        'chemdataextractor', 'pandas', 'elsapy', 'gensim', 'pymatgen'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Materials Science',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
)