from setuptools import setup, find_packages

version = '{{cookiecutter.version}}'

install_requires = []

setup(name='{{cookiecutter.repo_name}}',
      version=version,
      description="{{cookiecutter.description}}",
      long_description="""\
""",
      classifiers=[],
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=install_requires,
      zip_safe=False,
      )