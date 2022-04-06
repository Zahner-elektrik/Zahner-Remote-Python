from zahner_potentiostat.scpi_control.searcher import SCPIDeviceSearcher
from zahner_potentiostat.scpi_control.serial_interface import SerialCommandInterface, SerialDataInterface
from zahner_potentiostat.scpi_control.control import *
from zahner_potentiostat.scpi_control.datahandler import DataManager
from zahner_potentiostat.scpi_control.datareceiver import TrackTypes
from zahner_potentiostat.display.onlinedisplay import OnlineDisplay

from jupyter_utils import executionInNotebook
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

if __name__ == '__main__':
    deviceSearcher = SCPIDeviceSearcher()
    deviceSearcher.searchZahnerDevices()
    commandSerial, dataSerial = deviceSearcher.selectDevice()
    
    ZahnerPP2x2 = SCPIDevice(SerialCommandInterface(commandSerial), SerialDataInterface(dataSerial))

    ZahnerPP2x2.setAutorangingEnabled(True)
    ZahnerPP2x2.setInterpolationEnabled(True)
    ZahnerPP2x2.setRaiseOnErrorEnabled(True)
    
    ZahnerPP2x2.setSamplingFrequency(25)
    
    ZahnerPP2x2.calibrateOffsets()

    dataReceiver = ZahnerPP2x2.getDataReceiver()
    dataManager = DataManager(dataReceiver)
    
    onlineDisplay = None
    if executionInNotebook() == False:
        onlineDisplay = OnlineDisplay(dataReceiver)

    timeChargeCycleData = []
    timeDischargeCycleData = []
    
    voltageChargeCycleData = []
    voltageDischargeCycleData = []
    
    currentChargeCycleData = []
    currentDischargeCycleData = []
    
    currentsInCycles = [2.5, 5, 7.5]
    cycles = len(currentsInCycles)

    ZahnerPP2x2.setParameterLimitCheckToleranceTime(0.1)

    for i in range(cycles):
        print("cycle {} of {}".format(i+1, cycles))
        
        """
        Constant voltage phase
        """
        ZahnerPP2x2.setCoupling(COUPLING.POTENTIOSTATIC)
        ZahnerPP2x2.setVoltageParameterRelation(RELATION.ZERO)
        ZahnerPP2x2.setVoltageParameter(1)
        ZahnerPP2x2.setMaximumTimeParameter("60 s")
        ZahnerPP2x2.measurePolarization()
        dataReceiver.deletePoints()

        """
        Charge phase
        """
        ZahnerPP2x2.measureCharge(current = np.abs(currentsInCycles[i]),
                                  stopVoltage = 2,
                                  maximumTime = "4 min")
    
        completeData = dataReceiver.getCompletePoints() 
        timeData = completeData[TrackTypes.TIME.toString()]
        voltageData = completeData[TrackTypes.VOLTAGE.toString()]
        currentData = completeData[TrackTypes.CURRENT.toString()]
        dataReceiver.deletePoints()
    
        timeChargeCycleData.append(timeData)
        voltageChargeCycleData.append(voltageData)
        currentChargeCycleData.append(currentData)
        
        """
        Discharge phase
        """
        ZahnerPP2x2.measureDischarge(current = -1 * np.abs(currentsInCycles[i]),
                                     stopVoltage = 1,
                                     maximumTime = "4 min")
    
        completeData = dataReceiver.getCompletePoints() 
        timeData = completeData[TrackTypes.TIME.toString()]
        voltageData = completeData[TrackTypes.VOLTAGE.toString()]
        currentData = completeData[TrackTypes.CURRENT.toString()]
        dataReceiver.deletePoints()
    
        timeDischargeCycleData.append(timeData)
        voltageDischargeCycleData.append(voltageData)
        currentDischargeCycleData.append(currentData)

    if onlineDisplay != None:
        onlineDisplay.close()
    
    ZahnerPP2x2.close()

    chargeWhileCharging = []
    chargeWhileDischarging = []
        
    for cycle in range(cycles):
        lastTimeStamp = 0
        sumOfChargeInCycle = 0
        
        for i in range(len(timeChargeCycleData[cycle])):
            timeDelta = timeChargeCycleData[cycle][i] - lastTimeStamp
            lastTimeStamp = timeChargeCycleData[cycle][i]
            charge = currentChargeCycleData[cycle][i] * timeDelta
            
            sumOfChargeInCycle += charge
        
        chargeWhileCharging.append(sumOfChargeInCycle)
    
    for cycle in range(cycles):
        lastTimeStamp = 0
        sumOfChargeInCycle = 0
        
        for i in range(len(timeDischargeCycleData[cycle])):
            timeDelta = timeDischargeCycleData[cycle][i] - lastTimeStamp
            lastTimeStamp = timeDischargeCycleData[cycle][i]
            charge = currentDischargeCycleData[cycle][i] * timeDelta
            
            sumOfChargeInCycle += charge
        
        chargeWhileDischarging.append(sumOfChargeInCycle)

    coulombicEfficiency = []
    
    for cycle in range(cycles):
        efficiency = np.abs(chargeWhileDischarging[cycle] / chargeWhileCharging[cycle]) * 100
        coulombicEfficiency.append(efficiency)
        print("Current: {:.2f} A\tEfficiency: {:.2f} %".format(currentsInCycles[cycle], efficiency))

    figure, (chargeAxis, dischargeAxis, table) = plt.subplots(3, 1, figsize=[14,8])
    figure.suptitle("Cycles")
    
    for cycle in range(cycles):
        chargeAxis.plot(timeChargeCycleData[cycle], voltageChargeCycleData[cycle], label="{:.1f} A current".format(np.abs(currentsInCycles[cycle])))
        dischargeAxis.plot(timeDischargeCycleData[cycle], voltageDischargeCycleData[cycle], label="{:.1f} A current".format(np.abs(currentsInCycles[cycle])))
        
    chargeAxis.get_shared_x_axes().join(chargeAxis, dischargeAxis)
    
    chargeAxis.set_ylabel("Voltage / V")
    chargeAxis.grid(which="both")
    plt.setp(chargeAxis.get_xticklabels(), visible=False)
    
    dischargeAxis.set_xlabel("Time / s")
    dischargeAxis.set_ylabel("Voltage / V")
    dischargeAxis.grid(which="both")
    
    chargeAxis.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc="lower left", ncol=3, mode="expand", borderaxespad=0.0)
    
    table.axis("off")
    collabel = ["Current of Cycle", "Coulombic Efficiency of Cycle"]
    cellText = [["{:.1f} A".format(current) for current in currentsInCycles], ["{:.2f} %".format(coulombic) for coulombic in coulombicEfficiency]]
    cellText = np.transpose(cellText)
    table.table(cellText=cellText, colLabels=collabel, loc="center", rowLoc="center", cellLoc="center")
    
    plt.show()
    
    figure.savefig("ChargingCycles.svg")

