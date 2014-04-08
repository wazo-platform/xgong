from setuptools import setup, find_packages

version = '0.1'

setup(name='jenkins_gong',
      version=version,
      description="Ring a gong when jenkins fails",
      long_description="""\
""",
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Gregory Eric Sanderson',
      author_email='gsanderson@avencall.com',
      url='http://github.com/xivo-pbx/jenkins-gong',
      license='GPL3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'requests'
      ],
      entry_points={
          'console_scripts': [
              'jenkins_gong = jenkins_gong.main:main'
          ]
      }
      )
