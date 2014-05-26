from distutils.core import setup
import os

if os.name == 'nt':
    import py2exe

setup(console=['ffmpeg_cli.py'])