import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(
    name="resilient_code",
    version="0.2.0",
    description="Decorators and helpers to make code resilient",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lohjine/resilient_code",
    author="Loh Jin-E",
    author_email="mail@lohjine.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires='>=3.6',
)
