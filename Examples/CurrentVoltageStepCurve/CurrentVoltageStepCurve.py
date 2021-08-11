from zahner_potentiostat.scpi_control.searcher import SCPIDeviceSearcher
from zahner_potentiostat.scpi_control.serial_interface import SerialCommandInterface, SerialDataInterface
from zahner_potentiostat.scpi_control.control import *
from zahner_potentiostat.scpi_control.datahandler import DataManager
from zahner_potentiostat.scpi_control.datareceiver import TrackTypes
from zahner_potentiostat.display.dcplot import DCPlot
from zahner_potentiostat.display.onlinedisplay import OnlineDisplay

from jupyter_utils import executionInNotebook, notebookCodeToPython
if __name__ == '__main__':
    deviceSearcher = SCPIDeviceSearcher()
    deviceSearcher.searchZahnerDevices()
    commandSerial, dataSerial = deviceSearcher.selectDevice()
    ZahnerXPOT2 = SCPIDevice(SerialCommandInterface(commandSerial), SerialDataInterface(dataSerial))
    ZahnerXPOT2.clearState()

    ZahnerXPOT2.setRaiseOnErrorEnabled(True)
    ZahnerXPOT2.calibrateOffsets()
    ZahnerXPOT2.setSamplingFrequency(50)
    
    ZahnerXPOT2.setAutorangingEnabled(True)
    ZahnerXPOT2.setInterpolationEnabled(True)
    
    ZahnerXPOT2.setShuntIndex(1)
    ZahnerXPOT2.setVoltageRangeIndex(0)

    onlineDisplay = None
    if executionInNotebook() == False:
        onlineDisplay = OnlineDisplay(ZahnerXPOT2.getDataReceiver(), displayConfiguration="UlogI")

    ZahnerXPOT2.setCoupling(COUPLING.POTENTIOSTATIC)
    ZahnerXPOT2.setVoltageRelation(RELATION.ZERO)
    ZahnerXPOT2.setVoltageParameterRelation(RELATION.ZERO)

    ZahnerXPOT2.setVoltageValue(0)

    ZahnerXPOT2.setMinimumCurrentParameter(-0.5)
    ZahnerXPOT2.setMaximumCurrentParameter(+0.5)
    ZahnerXPOT2.setMinMaxCurrentParameterCheckEnabled(True)

    ZahnerXPOT2.setAbsoluteTolerance(0.000)
    ZahnerXPOT2.setRelativeTolerance(0.001)
    ZahnerXPOT2.setToleranceBreakEnabled(True)
    
    ZahnerXPOT2.setMinimumTimeParameter(1)
    ZahnerXPOT2.setMaximumTimeParameter(10)

    ZahnerXPOT2.setStepSize(0.01)
    ZahnerXPOT2.setVoltageParameter(2)

    ZahnerXPOT2.measureIEStairs()

    dataReceiver = ZahnerXPOT2.getDataReceiver()
    dataManager = DataManager(dataReceiver)
    dataManager.plotTIUData()

    completeData = dataReceiver.getCompletePoints() 
    voltageData = completeData[TrackTypes.VOLTAGE.toString()]
    currentData = completeData[TrackTypes.CURRENT.toString()]
    
    display = DCPlot("Current voltage curve", "Voltage", "V", [{"label": "Current", "unit": "A", "name": "Current", "log": True}],[voltageData, [currentData]])
    display.savePlot("current_voltage_curve.pdf")

    dataReceiver.deletePoints()
    ZahnerXPOT2.setMinMaxCurrentParameterCheckEnabled(False)

    ZahnerXPOT2.setCoupling(COUPLING.GALVANOSTATIC)
    ZahnerXPOT2.setCurrentValue(0)

    ZahnerXPOT2.setToleranceBreakEnabled(False)
    ZahnerXPOT2.setMaximumTimeParameter(1)

    ZahnerXPOT2.setStepSize(0.01)
    ZahnerXPOT2.setCurrentParameter(0.5)

    ZahnerXPOT2.measureIEStairs()

    dataManager.plotTIUData()

    if onlineDisplay != None:
        onlineDisplay.close()
    
    ZahnerXPOT2.close()
    print("finish")

    if executionInNotebook() == True:
        notebookCodeToPython("CurrentVoltageStepCurve.ipynb")

