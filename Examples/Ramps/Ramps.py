from zahner_potentiostat.scpi_control.searcher import SCPIDeviceSearcher
from zahner_potentiostat.scpi_control.serial_interface import SerialCommandInterface, SerialDataInterface
from zahner_potentiostat.scpi_control.control import *
from zahner_potentiostat.scpi_control.datahandler import DataManager
from zahner_potentiostat.scpi_control.datareceiver import TrackTypes
from zahner_potentiostat.display.onlinedisplay import OnlineDisplay

from jupyter_utils import executionInNotebook
if __name__ == '__main__':
    deviceSearcher = SCPIDeviceSearcher()
    deviceSearcher.searchZahnerDevices()
    commandSerial, dataSerial = deviceSearcher.selectDevice()
    ZahnerPP2x2 = SCPIDevice(SerialCommandInterface(commandSerial), SerialDataInterface(dataSerial))
    ZahnerPP2x2.clearState()

    ZahnerPP2x2.setRaiseOnErrorEnabled(True)
    ZahnerPP2x2.calibrateOffsets()
    ZahnerPP2x2.setSamplingFrequency(10)
    
    ZahnerPP2x2.setAutorangingEnabled(True)
    ZahnerPP2x2.setInterpolationEnabled(True)
    
    ZahnerPP2x2.setShuntIndex(1)
    ZahnerPP2x2.setVoltageRangeIndex(0)

    ZahnerPP2x2.setMinimumCurrentGlobal(-8)
    ZahnerPP2x2.setMaximumCurrentGlobal(4)
    ZahnerPP2x2.setGlobalCurrentCheckEnabled(True)
    
    ZahnerPP2x2.setMinimumVoltageGlobal(3.0)
    ZahnerPP2x2.setMaximumVoltageGlobal(4.25)
    ZahnerPP2x2.setGlobalVoltageCheckEnabled(True)
    
    ZahnerPP2x2.setGlobalLimitCheckToleranceTime(1)

    onlineDisplay = None
    if executionInNotebook() == False:
        onlineDisplay = OnlineDisplay(ZahnerPP2x2.getDataReceiver())

    ZahnerPP2x2.setCoupling(COUPLING.POTENTIOSTATIC)

    ZahnerPP2x2.setVoltageRelation(RELATION.OCV)
    ZahnerPP2x2.setVoltageParameterRelation(RELATION.ZERO)

    openCircuitVoltage = ZahnerPP2x2.measureOCV()
    print("open circuit reference voltage: " + str(openCircuitVoltage) + " V")

    ZahnerPP2x2.setVoltageValue(0)

    BatteryC = 2.6
    ZahnerPP2x2.setMinimumCurrentParameter(-2.0 * BatteryC)
    ZahnerPP2x2.setMaximumCurrentParameter(1.0 * BatteryC)
    ZahnerPP2x2.setParameterLimitCheckToleranceTime(0.5)
    ZahnerPP2x2.setMinMaxCurrentParameterCheckEnabled(True)

    ZahnerPP2x2.setScanRateParameter(0.010)

    ZahnerPP2x2.measureRampValueInScanRate(targetValue = 4.2)
    ZahnerPP2x2.measureRampValueInScanRate(targetValue = 3.0)

    ZahnerPP2x2.setVoltageParameterRelation(RELATION.OCV)

    ZahnerPP2x2.measureRampValueInScanRate(targetValue =  0.0)

    dataReceiver = ZahnerPP2x2.getDataReceiver()
    dataManager = DataManager(dataReceiver)
    dataManager.plotTIUData()

    if onlineDisplay != None:
        onlineDisplay.close()
    
    ZahnerPP2x2.close()
    print("finish")

