from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pycoornet",
    version="0.1",
    description="Using Python Given a set of URLs, this packages detects coordinated link sharing behavior on social media and outputs the network of entities that performed such behaviour.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PyCooRnet developer group",
    url="https://github.com/UPB-SS1/PyCooRnet",
    packages=find_packages(exclude=["test", "*.test", "*.tes.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    keywords="pyCooRnet",
    license="MIT",
    test_suite="test",
)
