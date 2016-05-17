from setuptools import setup, find_packages

setup(name='cartographer',
      version='0.1.0',
      description='Python library for using JSON API, especially with Flask.',
      url='http://github.com/Patreon/cartographer',
      author='Patreon',
      author_email='david@patreon.com',
      license='Apache 2.0',
      packages=find_packages(exclude=['example', 'example.*', 'test', 'test.*']),
      install_requires=[
          'python-dateutil==2.4.2',
          'ciso8601==1.0.1'
      ],
      zip_safe=True,
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Web Environment',
          'Framework :: Flask',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ]
)
