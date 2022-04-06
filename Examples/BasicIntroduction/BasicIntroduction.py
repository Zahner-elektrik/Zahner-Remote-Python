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
    commandSerial, dataSerial = deviceSearcher.selectDevice("33000")

    ZahnerPP2x2 = SCPIDevice(SerialCommandInterface(commandSerial), SerialDataInterface(dataSerial))

    onlineDisplay = None
    if executionInNotebook() == False:
        onlineDisplay = OnlineDisplay(ZahnerPP2x2.getDataReceiver())

    ZahnerPP2x2.setSamplingFrequency(25)
    ZahnerPP2x2.setCoupling(COUPLING.POTENTIOSTATIC)

    ZahnerPP2x2.setMaximumTimeParameter(15)

    ZahnerPP2x2.setVoltageParameter(0)
    ZahnerPP2x2.measurePolarization()
    
    ZahnerPP2x2.setVoltageParameter(3)
    ZahnerPP2x2.measurePolarization()
    
    ZahnerPP2x2.setVoltageParameter(0)
    ZahnerPP2x2.measurePolarization()

    dataReceiver = ZahnerPP2x2.getDataReceiver()

    completeData = dataReceiver.getCompletePoints()

    timeData = completeData[TrackTypes.TIME.toString()]
    voltageData = completeData[TrackTypes.VOLTAGE.toString()]
    currentData = completeData[TrackTypes.CURRENT.toString()]
    
    print(currentData[0:10])

    dataManager = DataManager(dataReceiver)
    dataManager.plotTIUData("polarization.pdf",10,5)

    dataManager.saveDataAsText("polarization.txt")

    if onlineDisplay != None:
        onlineDisplay.close()
    
    ZahnerPP2x2.close()
    print("finish")

