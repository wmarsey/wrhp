from distutils.core import setup, Extension

module = Extension('fastlev',
                    sources = ['fastlev.cpp'])

setup (name = 'fastlev',
       version = '1.0',
       description = 'This is a first try fastlev package',
       ext_modules = [module])
