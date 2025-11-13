import setuptools

descx = '''

  Python calendar

    #"calfile.py",  "calutils.py",  "pyala.py",
    #"pycal.py", "calfsel.py", "comline.py", "pycalent.py",
    #"pycallog.py",  "pycalsql.py",
    #],

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

def get_doclist():
    doclist = []; droot = "docs/"
    doclistx = os.listdir(droot)
    for aa in doclistx:
        doclist.append("docs/" + aa)
    #print("doclist:", doclist) ; sys.exit()
    return doclist

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
    version=get_version("pycalgui.py"),
    author="Peter Glen",
    author_email="peterglen99@gmail.com",
    description="Python Calendar.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pglen/pycal",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(include=includex),

    scripts = ["pycalgui.py", "pycaldump.py", ],

    include_package_data=True,
    package_dir = {
                    'pyvcal' : 'pyvcal',
                    'images' : 'pyvcal/images',
                  },
    package_data = {
                   # "docs": get_doclist(),
                    "pyvcal" : ["astrocal.ics", "holiday.ics",],
                    "pyvcal/images" : ['images/*.png',],
                  },


    #data_files =  [
    #                ("pyvcal/images", ['images/pycal.png',])
    #              ],

    #py_modules = ['pyvcal'],

    install_requires=deplist,
    python_requires='>=3',
    entry_points={
        'console_scripts': [
                            "pycalgui=pycalgui:mainfunc",
                            "pycaldump=pycaldump:mainfunc",
                            ],
    }
)


# EOF
