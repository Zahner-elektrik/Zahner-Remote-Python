![Zahner-Remote-Python](https://doc.zahner.de/github_resources/Zahner-Remote-Python.png)

The repository Zahner-Remote-Python contains examples for using the Python package [zahner_potentiostat](https://github.com/Zahner-elektrik/zahner_potentiostat) to control the [Zahner Potentiostats](https://zahner.de/products#external-potentiostats) **PP212, PP222, PP242, EL1002 or XPOT2** via USB **without** a Zennium connected via EPC.

The package was developed to **easily integrate** external Zahner Potentiostats into Python scripts for more **complex measurement** tasks and for **automation purposes**.

The control concept is that there are different primitives which can be combined for different electrochemical measurement methods. These primitives can all be configured differently to match the application. In the [API documentation](https://doc.zahner.de/zahner_potentiostat/index.html) of the respective function all possible configuration setter methods are listed.

> [!NOTE]  
> **For this library, the computer must be connected to the PP212, PP222, PP242, EL1002 or XPOT2 via USB. These devices are then controlled directly via USB, without EPC and without Zennium. AC methods are not available with this library. For AC methods like EIS a [Zennium](https://zahner.de/products#potentiostats) with [EPC](https://zahner.de/products-details/addon-cards/epc42) and the [thales_remote](https://github.com/Zahner-elektrik/Thales-Remote-Python) library is necessary.**

**The following [primitives](https://en.wikipedia.org/wiki/Language_primitive) are available to compose methods with:**  

* Potentiostatic or galvanostatic polarization  
  * [measurePolarization()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measurePolarization)  
* Open circuit voltage/potential scan  
  * [measureOCV()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measureOCV)  
  * [measureOCVScan()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measureOCVScan)  
* Ramps potentiostatic or galvanostatic  
  * [measureRampValueInTime()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measureRampValueInTime)  
  * [measureRampValueInScanRate()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measureRampValueInScanRate)  
  * [measureRampScanRateForTime()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measureRampScanRateForTime)  
* Staircase potentiostatic or galvanostatic  
  * [measureIEStairs()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measureIEStairs)  
  
**And as an example, the following methods were developed from the primitives:**  

* Charge or discharge something  
  * [measureCharge()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measureCharge)  
  * [measureDischarge()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measureDischarge)  
* Output potentiostatic or galvanostatic profile as potentiostatic or galvanostatic polarizations or ramps  
  * [measureProfile()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measureProfile)  
* PITT Potentiostatic Intermittent Titration Technique  
  * [measurePITT()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measurePITT)  
* GITT Galvanostatic Intermittent Titration Technique  
  * [measureGITT()](https://doc.zahner.de/zahner_potentiostat/scpi_control/control.html#zahner_potentiostat.scpi_control.control.SCPIDevice.measureGITT)  

This repository explains how to use the library with examples.
These examples build on each other and you should start with the first one.

# 📚 Documentation

The complete documentation of the individual functions can be found on the [API documentation website](https://doc.zahner.de/zahner_potentiostat/).  

# 🔧 Installation

For all examples the package [zahner_potentiostat](https://github.com/Zahner-elektrik/zahner_potentiostat) is required.  
The package can be installed via pip.

```
pip install zahner_potentiostat
```

You can clone the complete repository, or download only single examples.  
Each example consists of a Jupyter notebook with detailed documentation and explanations and a .py file containing only the Python source code from the notebook.

The Python source code is automatically extracted at the end of the Jupyter notebook. This source code can then be run with an IDE for easier development.

# 🔨 Basic Usage

```python
"""
Search the Zahner Potentiostat
"""
deviceSearcher = SCPIDeviceSearcher()
deviceSearcher.searchZahnerDevices()
commandSerial, dataSerial = deviceSearcher.selectDevice("35000")

"""
Connect to the Potentiostat
"""
ZahnerPP2x2 = SCPIDevice(SerialCommandInterface(commandSerial), SerialDataInterface(dataSerial))

"""
Setup measurement
"""
ZahnerPP2x2.setSamplingFrequency(10)
ZahnerPP2x2.setCoupling(COUPLING.POTENTIOSTATIC)
ZahnerPP2x2.setMaximumTimeParameter(15)

"""
Start measurement
"""
ZahnerPP2x2.setVoltageParameter(0)
ZahnerPP2x2.measurePolarization()
```

# 📖 Examples

The following examples all build on each other, you should read and understand them in sequence.

If images or text files are saved from the examples, then they are located in the same directory.

### [BasicIntroduction.ipynb](https://github.com/Zahner-elektrik/Zahner-Remote-Python/blob/main/Examples/BasicIntroduction/BasicIntroduction.ipynb)

* Search devices automatically
* Connect to a device
* Perform measurements
* Read and plot data

### [Polarizations.ipynb](https://github.com/Zahner-elektrik/Zahner-Remote-Python/blob/main/Examples/Polarizations/Polarizations.ipynb)

* Perform offset calibration
* Set the line frequency
* Set software current and voltage limits of the potentiostat
* Configure and use polarization primitive
* Configure and use the open circuit scan primitive
* Charge and discharge with the polarization primitive

### [Ramps.ipynb](https://github.com/Zahner-elektrik/Zahner-Remote-Python/blob/main/Examples/Ramps/Ramps.ipynb)

* Configure and use the ramps primitive
* Start a primitive at open circuit voltage

### [CurrentVoltageStepCurve.ipynb](https://github.com/Zahner-elektrik/Zahner-Remote-Python/blob/main/Examples/CurrentVoltageStepCurve/CurrentVoltageStepCurve.ipynb)

* Configure and use the staircase primitive
* Plotting with a logarithmic current axis

### [ArbitraryProfile.ipynb](https://github.com/Zahner-elektrik/Zahner-Remote-Python/blob/main/Examples/ArbitraryProfile/ArbitraryProfile.ipynb)

* Example of the composition of primitives for more complex measurement methods, with an arbitrary profile consisting of a sequence of primitives as example
* Limiting the shunt area

### [PITTandGITT.ipynb](https://github.com/Zahner-elektrik/Zahner-Remote-Python/blob/main/Examples/PITTandGITT/PITTandGITT.ipynb)

* Example of the composition of primitives for more complex measurement methods, with PITT and GITT as examples

### [CoulombicEfficiency.ipynb](https://github.com/Zahner-elektrik/Zahner-Remote-Python/blob/main/Examples/CoulombicEfficiency/CoulombicEfficiency.ipynb)

* Charging and discharging of a supercab with methods developed from primitives
* Calculate the charge by integrating the current in Python
* Display the charge efficiency depending on the current in a table with the corresponding charge and discharge voltage curves in a figure

## [ImpedanceMultiCellCycle.ipynb](https://github.com/Zahner-elektrik/Thales-Remote-Python/tree/main/Examples/ImpedanceMultiCellCycle/ImpedanceMultiCellCycle.ipynb)

* Multichannel operation with several external potentiostats, of the latest generation, type **PP2x2, XPOT2 or EL1002**
* Shared [Zennium series](https://zahner.de/products#potentiostats) device for impedance measurements
* Operation of the power potentiostats standalone without thales with the Python package [zahner_potentiostat](https://github.com/Zahner-elektrik/zahner_potentiostat)

## [ImpedanceRampHotSwap.ipynb](https://github.com/Zahner-elektrik/Thales-Remote-Python/tree/main/Examples/ImpedanceRampHotSwap/ImpedanceRampHotSwap.ipynb)

* Switch between Thales/EPC and SCPI/standalone operation of the external potentiostats (PP2x2, XPOT2 or EL1002) **without switching off the potentiostat**
* Shared [Zennium series](https://zahner.de/products#potentiostats) device for impedance measurements
* Operation of the power potentiostats standalone without thales with the Python package [zahner_potentiostat](https://github.com/Zahner-elektrik/zahner_potentiostat)

# 📧 Having a question?

Send an <a href="mailto:support@zahner.de?subject=Zahner-Remote-Python Question&body=Your Message">e-mail</a> to our support team.

# ⁉️ Found a bug or missing a specific feature?

Feel free to **create a new issue** with a respective title and description on the the [Zahner-Remote-Python](https://github.com/Zahner-elektrik/Zahner-Remote-Python/issues) repository.  
If you already found a solution to your problem, **we would love to review your pull request**!

# ✅ Requirements

Programming is done with the latest Python version at the time of commit.

The package [zahner_potentiostat](https://github.com/Zahner-elektrik/zahner_potentiostat) is required for communication with the device. The packages matplotlib, scipy and numpy are used to display the measurement results. Jupyter is not necessary, since each example is also available as a Python file.
