#!/usr/bin/env python3
import re
from setuptools import setup, find_packages
from pathlib import Path

# Project root
here = Path(__file__).parent.resolve()

# Extract version from app/liveresultscapture.py
version = "0.0.0"
module_path = here / 'app' / 'liveresultscapture.py'
#print(f"Reading version from {module_path}")
with module_path.open('r', encoding='utf-8') as f:
    for line in f:
        m = re.match(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", line)
        if m:
            version = m.group(1)
            break
#print(f"Extracted version: {version}")
# Long description from README.md
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='liveresultscapture',
    version=version,
    description='Live results capture for CrossMgr events',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='stuart.lynne@gmail.com',
    url='https://github.com/stuartlynne/liveresultscapture',
    packages=find_packages(include=['app', 'app.*']),
    package_dir={'app': 'app'},
    entry_points={
        'console_scripts': [
            'liveresultscapture=app.liveresultscapture:main',
        ],
    },
    install_requires=[
        'websocket-client',
    ],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)

