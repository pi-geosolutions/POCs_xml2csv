from setuptools import setup, find_packages

setup(
    name='pocs_xml2csv',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        pocs_xml2csv=src.pocs_xml2csv:pocs_xml2csv
    ''',
)