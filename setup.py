import setuptools

setuptools.setup(
    name="oilanalytics",
    version="0.0.9",
    author="aeorxc",
    description="Utilities for oil analytics",
    url="https://github.com/aeorxc/oilanalytics",
    project_urls={
        "Source": "https://github.com/aeorxc/oilanalytics",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas", "requests", "commodutil", "python-dotenv"],
    python_requires=">=3.8",
    setup_requires=["pytest-runner"],
    tests_requirer=["pytest"],
)
