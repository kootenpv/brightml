""" File unrelated to the package, except for convenience in deploying """
import re
import sh
import os

os.system("rm -rf dist/")
os.system("python setup.py sdist bdist_wheel")
os.system("twine upload dist/*")
