import setuptools

setuptools.setup(
    name="oilanalytics",
    version="0.1.23",
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
    install_requires=["pandas", "requests", "commodutil", "commodplot", "python-dotenv", "cachetools",
                      "beautifulsoup4"],
    python_requires=">=3.8",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    package_data={'oilanalytics': ['prices/templates/*.html', 'freight/templates/*.html']},
    include_package_data=True,
)
