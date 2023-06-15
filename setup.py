from setuptools import setup

setup(
    name='peewee-jsonfield',
    version='0.0.4',
    description='JSONField for Peewee',
    packages=['jsonfield'],
    install_requires=[
        'peewee',
        'pymysql'
    ],
    license='MIT License',
    platforms=['any'],
    author='Mark Smirnov',
    author_email='mark@mark99.ru'
)