# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='PyOscilloskop',
      version = '0.2.0',
      description = '',
      long_description = '',
      author = 'Philipp Klaus',
      author_email = 'philipp.l.klaus@web.de',
      url = '',
      license = 'GPL',
      packages = ['pyoscilloskop', 'pyoscilloskop.webapp'],
      scripts = ['scripts/rigolCli.py', 'scripts/pyoscilloskop-web'],
      include_package_data = True,
      zip_safe = True,
      platforms = 'any',
      requires = ['universal_usbtmc'],
      keywords = 'usbtmc Rigol Oscilloscope Function-Generator',
      classifiers = [
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GPL License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Topic :: System :: Monitoring',
          'Topic :: System :: Logging',
      ]
)


