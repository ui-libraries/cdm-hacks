## Setting up a Python Environment

####Installing Python
Instructions on installing Python are at [http://www.python.org/downloads/](http://www.python.org/downloads/). If you're installing on Windows, make sure you download the right installation for your machine (32-bit or 64-bit). You may need to [add the path to Python to your system environment variables](http://geekswithblogs.net/renso/archive/2009/10/21/how-to-set-the-windows-path-in-windows-7.aspx) (requires admin permissions).  

**Which version?**  If you plan to use any of the scripts in cdm-hacks, or if you plan to use the pycdm module for interacting with the CONTENTcm API, install 2.7.x  

####Installing pip
pip is a package installer for Python that allows you to download and install third-party modules with a single command. To install pip:
* First try instructions at: http://www.pip-installer.org/en/latest/installing.html (tl;dr: open a command-line window and run: python get-pip.py)
* If you are on Windows, you may need to add the path to your Python "Scripts" directory (ex., "C:\Python27\Scripts") to your [PATH in your system environment variables](http://geekswithblogs.net/renso/archive/2009/10/21/how-to-set-the-windows-path-in-windows-7.aspx) (requires admin permissions).  

If that didn't work, then:  

* Install [setup-tools](https://pypi.python.org/pypi/setuptools), documentation at http://pythonhosted.org//setuptools/
* If you are on 64-bit Windows, you may need to follow instructions here: [http://stackoverflow.com/questions/3652625/installing-setuptools-on-64-bit-windows](http://stackoverflow.com/questions/3652625/installing-setuptools-on-64-bit-windows)
* If you are on Windows, you may need to add the path to your Python "Scripts" directory (ex., "C:\Python27\Scripts") to your [PATH in your system environment variables](http://geekswithblogs.net/renso/archive/2009/10/21/how-to-set-the-windows-path-in-windows-7.aspx) (requires admin permissions).
* Install pip from: http://www.pip-installer.org/en/latest/installing.html

####Installing pycdm
pycdm is a Python module for working with the CONTENTdm API. More explanation, instructions, and sample scripts available at: [https://github.com/saverkamp/pycdm](https://github.com/saverkamp/pycdm). To install, open a command-line window and run:

    pip install pycdm

To upgrade pycdm, run:

    pip install pycdm --upgrade

