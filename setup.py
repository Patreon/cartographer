from setuptools import setup, find_packages

setup(name='cartographer',
      version='0.0.5',
      description='Python library for using JSON API with Flask.',
      url='http://github.com/Patreon/cartographer',
      author='Patreon',
      author_email='david@patreon.com',
      license='MIT',
      packages=find_packages(exclude=['example', 'example.*', 'test', 'test.*']),
      install_requires=[
          'python-dateutil==2.4.2',
          'ciso8601==1.0.1'
      ],
      zip_safe=True)
