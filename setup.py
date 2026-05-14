from setuptools import setup, find_packages

setup(
    name='pytbl',
    version='0.0.1',
    description='A personal library for stuff i got tired of doing again and again',
    long_description=open('USAGE.md').read(),
    long_description_content_type='text/markdown',
    author='TBL',
    author_email='tim.b.lukas@gmail.com',
    packages=find_packages(),
    install_requires=[
        "pytest"
    ],
    license='MIT',
    python_requires='>=3.7',
)
