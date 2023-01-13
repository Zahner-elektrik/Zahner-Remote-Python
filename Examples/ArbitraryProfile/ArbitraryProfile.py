from zahner_potentiostat.scpi_control.searcher import SCPIDeviceSearcher
from zahner_potentiostat.scpi_control.serial_interface import (
    SerialCommandInterface,
    SerialDataInterface,
)
from zahner_potentiostat.scpi_control.control import *
from zahner_potentiostat.scpi_control.datahandler import DataManager
from zahner_potentiostat.scpi_control.datareceiver import TrackTypes
from zahner_potentiostat.display.dcplot import DCPlot
from zahner_potentiostat.display.onlinedisplay import OnlineDisplay
from zahner_potentiostat.drivecycle.cycle_importer import (
    getNormalisedCurrentTableForNYCCCOL,
)

from jupyter_utils import executionInNotebook

if __name__ == "__main__":
    deviceSearcher = SCPIDeviceSearcher()
    deviceSearcher.searchZahnerDevices()
    commandSerial, dataSerial = deviceSearcher.selectDevice()
    ZahnerPP2x2 = SCPIDevice(
        SerialCommandInterface(commandSerial), SerialDataInterface(dataSerial)
    )
    ZahnerPP2x2.clearState()

    ZahnerPP2x2.setRaiseOnErrorEnabled(True)
    ZahnerPP2x2.calibrateOffsets()
    ZahnerPP2x2.setSamplingFrequency(20)

    ZahnerPP2x2.setAutorangingEnabled(False)
    ZahnerPP2x2.setInterpolationEnabled(False)

    ZahnerPP2x2.setShuntIndex(2)
    ZahnerPP2x2.setMinimumShuntIndex(2)
    ZahnerPP2x2.setMaximumShuntIndex(2)

    ZahnerPP2x2.setVoltageRangeIndex(0)

    onlineDisplay = None
    if executionInNotebook() == False:
        onlineDisplay = OnlineDisplay(ZahnerPP2x2.getDataReceiver())

    ZahnerPP2x2.setMinimumCurrentGlobal(-8)
    ZahnerPP2x2.setMaximumCurrentGlobal(4)
    ZahnerPP2x2.setGlobalCurrentCheckEnabled(True)

    ZahnerPP2x2.setMinimumVoltageGlobal(3.0)
    ZahnerPP2x2.setMaximumVoltageGlobal(4.25)
    ZahnerPP2x2.setGlobalVoltageCheckEnabled(True)

    ZahnerPP2x2.setGlobalLimitCheckToleranceTime(1)

    driveCycle = getNormalisedCurrentTableForNYCCCOL()
    driveCycle = driveCycle[0:245]

    ZahnerPP2x2.measureProfile(
        profileDict=driveCycle,
        coupling=COUPLING.GALVANOSTATIC,
        scalingFactor=-1.5,
        outputPrimitive="pol",
    )

    dataReceiver = ZahnerPP2x2.getDataReceiver()
    dataManager = DataManager(dataReceiver)
    dataManager.plotTIUData("profile.pdf", 10, 5)

    if onlineDisplay != None:
        onlineDisplay.close()

    ZahnerPP2x2.close()
    print("finish")
