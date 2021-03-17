import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ah-client",
    version="0.0.1",
    author="Jani Hietala",
    author_email="jani.hietala@vtt.fi",
    description="Arrowhead client library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VTT-OM/arrowhead-client",
    packages=["ah_client"],
    license="MIT",
    install_requires=["paho-mqtt", "requests"],
    extras_require={"dev": ["black", "pylint", "pycodestyle", "wheel"]},
    python_requires=">=3.8",
)
