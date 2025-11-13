import setuptools

descx = '''
  Python calendar
'''

import os, sys

def get_version(fname):
    ''' Get version number from the main file '''
    fp = open(fname, "rt")
    vvv = fp.read(); fp.close()

    loc_vers =  '1.0.0'     # Default
    for aa in vvv.split("\n"):
        idx = aa.find("VERSION ")
        if idx == 0:        # At the beginning of line
            try:
                loc_vers = aa.split()[2].replace('"', "")
                break
            except: pass
    #print("loc_vers:", loc_vers); sys.exit()
    return loc_vers

deplist = ["pyvguicom"] ,

includex = ["pyvcal"]

classx = [
          'Development Status :: Mature',
          'Environment :: GUI',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Databases',
        ]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyvcal",
    version=get_version("pyvcalgui.py"),
    author="Peter Glen",
    author_email="peterglen99@gmail.com",
    description="Python Calendar.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pglen/pycal",
    classifiers=[
        "Programming Language :: Python :: 3",
        #"License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(include=includex),

    scripts = ["pyvcalgui.py", "pyvcalala.py", ],

    include_package_data=True,
    package_data = {
                    "pyvcal" : [
                                "docs/*"
                                "images/*.png"
                                "ics/*.ics"
                                ],
                  },
    package_dir = {
                    'pyvcal' : 'pyvcal',
                  },
    install_requires=deplist,
    python_requires='>=3',
    entry_points={
        'console_scripts':
            [
            "pycalgui=pycalgui:mainfunc",
            "pycalala=pycalala:mainfunc",
            ],
        }
)

# EOF
