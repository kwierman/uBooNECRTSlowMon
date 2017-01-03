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
## Usage 

Before using any of the features here, it's good to note that the file [settings.py](https://github.com/kwierman/uBooNECRTSlowMon/blob/master/SCMon/settings.py) can be used to configure this system. Either fork and change the desired value or install from source and modify on build. This is supposed to emulate the Django/wekzeuge-esque way of using local settings, minus the local settings.

The package ships with some scripts with which to start. It's good to note that these need to be run with `python` as opposed to using the pathized run time command. This is due to UPS being a poor excuse for virtualization.

### Running the scripts

Since these scripts are installed per-user, most of these are run via

~~~ bash
python ~/.local/bin/my_script.py
~~~

### [getepicsvalues.py](https://github.com/kwierman/uBooNECRTSlowMon/blob/master/scripts/getepicsvalues.py)

Gets the current values from EPICS and prints them via the root logger.

### [sc2csv.py](https://github.com/kwierman/uBooNECRTSlowMon/blob/master/scripts/sc2csv.py)

Dumps out the last `d` days up to `l` entries of influx entries into csv files.

### [sc2epicsdaemon.py](https://github.com/kwierman/uBooNECRTSlowMon/blob/master/scripts/sc2epicsdaemon.py)

Runs the daemonized app to continuously update the EPICS database from influx.

### [update_prod.py](https://github.com/kwierman/uBooNECRTSlowMon/blob/master/scripts/update_prod.py)

Manual run of the update process.

> Note: This last script hasn't been checked in a while.
