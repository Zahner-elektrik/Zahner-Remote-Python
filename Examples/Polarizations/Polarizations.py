from zahner_potentiostat.scpi_control.searcher import SCPIDeviceSearcher
from zahner_potentiostat.scpi_control.serial_interface import SerialCommandInterface, SerialDataInterface
from zahner_potentiostat.scpi_control.control import *
from zahner_potentiostat.scpi_control.datahandler import DataManager
from zahner_potentiostat.scpi_control.datareceiver import TrackTypes
from zahner_potentiostat.display.onlinedisplay import OnlineDisplay

from jupyter_utils import executionInNotebook, notebookCodeToPython
if __name__ == '__main__':
    deviceSearcher = SCPIDeviceSearcher()
    deviceSearcher.searchZahnerDevices()
    commandSerial, dataSerial = deviceSearcher.selectDevice()

    ZahnerPP2x2 = SCPIDevice(SerialCommandInterface(commandSerial), SerialDataInterface(dataSerial))

    ZahnerPP2x2.setRaiseOnErrorEnabled(True)
    ZahnerPP2x2.setSamplingFrequency(50)

    ZahnerPP2x2.setLineFrequency(50)

    ZahnerPP2x2.calibrateOffsets()

    ZahnerPP2x2.setAutorangingEnabled(True)
    ZahnerPP2x2.setInterpolationEnabled(True)
    
    ZahnerPP2x2.setShuntIndex(1)
    #or
    ZahnerPP2x2.setCurrentRange(20)
    
    ZahnerPP2x2.setMinimumShuntIndex(1)
    ZahnerPP2x2.setMaximumShuntIndex(3)

    ZahnerPP2x2.setVoltageRangeIndex(0)
    #or
    ZahnerPP2x2.setVoltageRange(2.5)

    ZahnerPP2x2.setMinimumCurrentGlobal(-30)
    ZahnerPP2x2.setMaximumCurrentGlobal(30)
    ZahnerPP2x2.setGlobalCurrentCheckEnabled(True)
    
    ZahnerPP2x2.setMinimumVoltageGlobal(0)
    ZahnerPP2x2.setMaximumVoltageGlobal(2.5)
    ZahnerPP2x2.setGlobalVoltageCheckEnabled(True)

    onlineDisplay = None
    if executionInNotebook() == False:
        onlineDisplay = OnlineDisplay(ZahnerPP2x2.getDataReceiver())

    ZahnerPP2x2.setAutorangingEnabled(False)
    ZahnerPP2x2.setShuntIndex(1)

    ZahnerPP2x2.setCoupling(COUPLING.POTENTIOSTATIC)

    ZahnerPP2x2.setVoltageRelation(RELATION.OCV)
    ZahnerPP2x2.setVoltageParameterRelation("OCV")

    ZahnerPP2x2.setAbsoluteTolerance(0.001)
    ZahnerPP2x2.setRelativeTolerance(0.000)
    ZahnerPP2x2.setToleranceBreakEnabled(True)

    ZahnerPP2x2.setMinimumTimeParameter(10)

    ZahnerPP2x2.setMaximumTimeParameter("1 m")

    ZahnerPP2x2.setVoltageValue(0)

    print("open circuit reference voltage: " + str(ZahnerPP2x2.measureOCV()) + " V")

    ZahnerPP2x2.setPotentiostatEnabled(True)
    
    ZahnerPP2x2.setVoltageParameter(0.1) #OCV + 0.1
    ZahnerPP2x2.measurePolarization()
    
    ZahnerPP2x2.setVoltageParameter(0) #OCV
    ZahnerPP2x2.measurePolarization()
    
    ZahnerPP2x2.setPotentiostatEnabled(False)

    dataReceiver = ZahnerPP2x2.getDataReceiver()
    dataManager = DataManager(dataReceiver)
    dataManager.plotTIUData()

    ZahnerPP2x2.setToleranceBreakEnabled(False)
    ZahnerPP2x2.setVoltageRelation(RELATION.ZERO)
    ZahnerPP2x2.setVoltageParameterRelation(RELATION.ZERO)
    dataReceiver.deletePoints()
    ZahnerPP2x2.setAutorangingEnabled(True)

    ZahnerPP2x2.setCoupling(COUPLING.GALVANOSTATIC)

    ZahnerPP2x2.setMaximumCharge(100)
    ZahnerPP2x2.setMinimumCharge(-50)
    ZahnerPP2x2.setChargeBreakEnabled(True)

    ZahnerPP2x2.setMaximumTimeParameter("2 m")

    ZahnerPP2x2.setCurrentParameter(2)
    ZahnerPP2x2.measurePolarization()    

    ZahnerPP2x2.setCurrentParameter(-2)
    ZahnerPP2x2.measurePolarization()

    dataManager.plotTIUData()

    ZahnerPP2x2.setChargeBreakEnabled(False)
    dataReceiver.deletePoints()

    ZahnerPP2x2.setCoupling(COUPLING.GALVANOSTATIC)

    ZahnerPP2x2.setMinimumVoltageParameter(1)
    ZahnerPP2x2.setMaximumVoltageParameter(2)
    ZahnerPP2x2.setMinMaxVoltageParameterCheckEnabled(True)

    ZahnerPP2x2.setMaximumTimeParameter("30 s")

    ZahnerPP2x2.setCurrentParameter(10)
    ZahnerPP2x2.measurePolarization()

    ZahnerPP2x2.setMinimumVoltageParameter(1)

    cycles = 2
    for i in range(cycles):
        ZahnerPP2x2.setCurrentParameter(-10)
        ZahnerPP2x2.measurePolarization()
        ZahnerPP2x2.setCurrentParameter(10)
        ZahnerPP2x2.measurePolarization()

    ZahnerPP2x2.setCurrentParameter(-10)
    ZahnerPP2x2.measurePolarization()

    dataManager.plotTIUData()

    ZahnerPP2x2.setMinMaxVoltageParameterCheckEnabled(False)
    dataReceiver.deletePoints()

    ZahnerPP2x2.setMaximumTimeParameter("2 min")
    ZahnerPP2x2.setSamplingFrequency(1)

    ZahnerPP2x2.measureOCVScan()

    dataManager.plotTIUData()

    if onlineDisplay != None:
        onlineDisplay.close()
    
    ZahnerPP2x2.close()
    print("finish")

    if executionInNotebook() == True:
        notebookCodeToPython("Polarizations.ipynb")


