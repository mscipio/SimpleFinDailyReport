from setuptools import setup, find_packages

setup(
    name='simplefin-daily-report',
    version='1.0.0',
    description='A scheduled Python script to fetch financial data via SimpleFIN and send a detailed HTML email report.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Michele Scipioni', 
    url='https://github.com/mscipio/SimpleFinDailyReport', 
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dotenv',
    ],
    entry_points={
        # Define command line entry points for installation via pip
        # NOTE: 'run_report_main' must be defined as a function in MAIN.py
        'console_scripts': [
            'run-report=MAIN:run_report_main',
            'exchange-token=SimpleFIN_token_exchange:main' 
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
    ],
    python_requires='>=3.8',
)
