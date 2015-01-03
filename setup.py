from distutils.core import setup
setup(
  name = 'pypecli',
  version = '1.1.1',
  description = 'Curly bracket-indented Python for command line oneliners',
  author = 'Jens Kristian Geyti',
  author_email = 'pype@jkg.dk',
  url = 'https://github.com/ircflagship2/pype',
  download_url = 'https://github.com/ircflagship2/pype/tarball/1.1.0',
  scripts = ['pype'],
  keywords = ['commandline', 'terminal', 'scripting', 'linux', 'sysadm'],
  classifiers = ['Environment :: Console',
  				 'Development Status :: 4 - Beta',
  				 'Intended Audience :: System Administrators',
  				 'License :: OSI Approved :: MIT License',
  				 'Topic :: Utilities'],
)
