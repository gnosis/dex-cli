from setuptools import setup

requirements = [
    "Click>=7.0",
    "gql>=0.3.0",
]

# with open("README.md", 'r') as f:
#     long_description = f.read()

setup(
   name='dFusion',
   version='0.1',
   description='dFusion CLI',
   #long_description=
   long_description=long_description,
   author='Gnosis',
   author_email='admin@gnosis.pm',
   keywords=['dex', 'defi', 'exchange', 'ethereum', 'dfusion', 'gnosis'],
   packages=[
     'src'
    ],
   install_requires=requirements,
   url='https://github.com/gnosis/dex-cli',
)
