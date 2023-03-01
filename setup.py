from distutils.core import setup

setup(
    name="tra-fugu",
    version="0.5.1",
    description="Translate Japanese and English texts into one another, by FuguMT Model",
    url="https://github.com/tos-kamiya/tra-fugu",
    author="Toshihiro Kamiya",
    author_email="kamiya@mbj.nifty.com",
    license="Unlicense",
    classifiers=[
        "License :: OSI Approved :: Unlicense",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=[
        "tra_fugu",
    ],
    include_package_data=True,
    install_requires=[
        "numpy", "sentencepiece", "torch", "transformers", "sacremoses",
        "guietta", "qt-material",
    ],
    entry_points={
        "console_scripts": [
            "tra-fugu=tra_fugu.cli:main",
            "tra-fugu-gui=tra_fugu.gui:main",
        ],
    },
)
