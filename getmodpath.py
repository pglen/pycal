#!/usr/bin/env python3
import  os, sys
mod = __import__(sys.argv[1])
print(os.path.dirname(os.path.realpath(mod.__file__)))
