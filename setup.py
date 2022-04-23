import setuptools

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="circuitsim",
    version="0.0.1",
    author="Ruben Purdy",
    author_email="rpurdy@andrew.cmu.edu",
    description="Run HDL simulations from python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=["Programming Language :: Python :: 3"],
    python_requires=">=3.6",
    install_requires=["circuitgraph>=0.2.0", "natsort"],
)
