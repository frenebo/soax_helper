import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="soax-helper",
    version="0.0.1",
    author="Paul Kreymborg Dogic Lab UCSB",
    author_email="kreymborg@ucsb.edu",
    description="Command line helper for using SOAX to find filaments in images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frenebo/soax_helper",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    scripts=['src/soax_helper']
)