from setuptools import setup, setuptools

requirements = [
    "Click>=7.0",
    "gql>=0.3.0",
]

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
  name='dFusion',
  version='0.1',
  description='dFusion CLI',
  license='MIT License',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author='anxolin',
  author_email='anxolin@gmail.com',
  keywords=['dex', 'defi', 'exchange', 'ethereum', 'dfusion', 'gnosis'],
  packages=setuptools.find_packages(),
  install_requires=requirements,
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  url='https://github.com/gnosis/dex-cli',
)
