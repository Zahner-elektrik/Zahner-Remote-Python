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
    ZahnerPP2x2.setSamplingFrequency(5)

    ZahnerPP2x2.setAutorangingEnabled(False)
    ZahnerPP2x2.setInterpolationEnabled(False)

    ZahnerPP2x2.setShuntIndex(2)
    ZahnerPP2x2.setMinimumShuntIndex(2)
    ZahnerPP2x2.setMaximumShuntIndex(2)

    ZahnerPP2x2.setVoltageRangeIndex(0)

    onlineDisplay = None
    if executionInNotebook() == False:
        onlineDisplay = OnlineDisplay(ZahnerPP2x2.getDataReceiver())

    ocVoltage = ZahnerPP2x2.measureOCV()
    print("open circuit reference voltage: " + str(ocVoltage) + " V")

    ZahnerPP2x2.measurePITT(
        targetVoltage=ocVoltage + 0.1,
        endVoltage=ocVoltage,
        stepVoltage=0.01,
        onTime="30s",
        openCircuitTime="30s",
        startWithOCVScan=True,
        measureOnTargetVoltage=True,
    )

    dataReceiver = ZahnerPP2x2.getDataReceiver()
    dataManager = DataManager(dataReceiver)
    dataManager.saveDataAsText("PITT.txt")
    dataManager.plotTIUData("PITT.png", 10, 5)

    dataReceiver.deletePoints()

    ZahnerPP2x2.measureGITT(
        targetVoltage=ocVoltage + 0.15,
        endVoltage=ocVoltage - 0.1,
        current=1,
        onTime="30s",
        openCircuitTime="30s",
        startWithOCVScan=True,
    )

    dataManager.saveDataAsText("GITT.txt")
    dataManager.plotTIUData("GITT.png", 10, 5)

    if onlineDisplay != None:
        onlineDisplay.close()

    ZahnerPP2x2.close()
    print("finish")
