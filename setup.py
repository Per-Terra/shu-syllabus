from setuptools import find_packages, setup

setup(
    name="shu_syllabus",
    version="0.1.0",
    description="This is a package for scraping the syllabus of Shunan University.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="per-terra",
    url="https://github.com/Per-Terra/shu-syllabus",
    packages=find_packages("src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "beautifulsoup4",
        "requests",
    ],
    python_requires=">=3.10",  # union types as X | Y is used (PEP 604)
)
