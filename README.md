# uBooNECRTSlowMon
MicroBooNE's Cosmic Ray Tagger Slow Control Monitor Interface Script

## Installation

As this is meant to run on the CRT machines, I highly recommend an installation from source.

It is important that this is run with the user that will be deploying the script. For instance, if `uboonepro` is the production user on the machine, then the package needs to be installed by uboonepro.

### Making sure that the UPS python is being used

The following commands can be used to activate the UPS python product. 

~~~ bash
source <product_dir>/setup
setup python v2_7_11
~~~

### The very janky method of using pip to install and manage dependencies

The python package manager, `pip` can be used to install the package on top of the UPS python via the user local package directory. This is wrapped in the following three lines:

~~~ bash
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py --user
~/.local/bin/pip install --user git+https://github.com/kwierman/uBooNECRTSlowMon
~~~

This only installs the package for the user. Using the examples is now as easy as:

~~~ bash
python ~/.local/bin/example.py
~~~
