from thales_remote.connection import ThalesRemoteConnection
from thales_remote.script_wrapper import PotentiostatMode,ThalesRemoteScriptWrapper
from thales_remote.error import TermConnectionError, ThalesRemoteError

from zahner_potentiostat.scpi_control.searcher import SCPIDeviceSearcher
from zahner_potentiostat.scpi_control.serial_interface import SerialCommandInterface, SerialDataInterface
from zahner_potentiostat.scpi_control.control import *
from zahner_potentiostat.scpi_control.datahandler import DataManager

import threading
import time

class EpcScpiHandlerFactory():
    """ Class for creating the control objects.
    
    This class initializes the connection to the zennium.  
    The :func:`~epc_scpi_handler.EpcScpiHandlerFactory.createEpcScpiHandler` method can then be used
    to create a control object for the corresponding device.
    
    :param shared_zennium_target: IP address at which the Zennium can be reached. Default is "localhost".
    """
    def __init__(self, shared_zennium_target = "localhost"):
        self._zenniumConnection = ThalesRemoteConnection()
        connectionSuccessful = self._zenniumConnection.connectToTerm(shared_zennium_target, "ScriptRemote")
        if connectionSuccessful == False:
            raise TermConnectionError("connection to zennium not possible")
        
        self.sharedZenniumInterface = ThalesRemoteScriptWrapper(self._zenniumConnection)
        self.sharedZenniumInterface.forceThalesIntoRemoteScript()
        self._handlerList = []
        return
        
    def getSharedZennium(self):
        """ Returns the zennium object.
        
        Returns the Zennium object, which contains the Remote2 commands as methods.
        
        :returns: Object with the Remote2 wrapper.
        :rtype: ThalesRemoteScriptWrapper
        """
        return self.sharedZenniumInterface
    
    def getZenniumConnection(self):
        """ Returns the zennium connection object.
        
        Returns the object that manages the connection to the zennium.
        
        :returns: Object with the connection to the zennium.
        :rtype: ThalesRemoteConnection
        """
        return self._zenniumConnection
    
    def createEpcScpiHandler(self, epcChannel, serialNumber):
        """ Returns the zennium connection object.
        
        This method initializes the external potentiostats and creates the objects.
        
        The objects are in SCPI mode after calling this function.
        For compatibility, the devices always start in EPC mode when connected to EPC, then they must
        be switched to SCPI standalone mode via Remote2. It is only possible to switch to SCPI mode via Remote2.
        
        :param epcChannel: Number of the EPC channel to which the device is connected via EPC cable.
            If a Rmux card is plugged in then the numbers have an offset.
        :param serialNumber: Serial number of the external potentiostat.
        :returns: Object with the external potentiostat.
        :rtype: EpcScpiHandler
        """
        newDevice = EpcScpiHandler(self.getSharedZennium(), epcChannel, serialNumber)
        
        deviceSearcher = SCPIDeviceSearcher()
        deviceSearcher.searchZahnerDevices()
        commandSerial, dataSerial = deviceSearcher.selectDevice(str(serialNumber))
        
        """
        If the device is not found, then it is checked whether it is found as an EPC device.
        If it is found as an EPC device, it is switched to SCPI mode.
        """
        if commandSerial == None and dataSerial == None:
            newDevice.acquireSharedZennium()
            newDevice.sharedZenniumInterface.selectPotentiostat(epcChannel)
            name, serial = newDevice.sharedZenniumInterface.getDeviceInformation()
            newDevice.releaseSharedZennium()
            
            if serial not in str(serialNumber):
                raise ThalesRemoteError("Potentiostat is not found on the EPC channel.")
                        
            newDevice.switchToSCPI()
        else:
            newDevice.connectSCPIDevice()
        
        listItem = dict()
        listItem["serial_number"] = serialNumber
        listItem["epc_channel"] = epcChannel
        listItem["hander_object"] = newDevice
        
        self._handlerList.append(listItem)
        
        return newDevice
    
    def closeAll(self):
        """ Close connections to all devices.
        
        This command closes all connections to the external potentiostats and to the Zennium.
        """
        for element in self._handlerList:
            element["hander_object"].close()
            
        self._handlerList = []
        
        self._zenniumConnection.disconnectFromTerm()
        return
        
    
class EpcScpiHandler():
    """ Class for the control objects.
    
    This class manages the object composed of a cennium and the external potentiostat.
    The object contains an instance of a :class:`~zahner_potentiostat.scpi_control.control.SCPIDevice`
    and the shared common :class:`~thales_remote.script_wrapper.ThalesRemoteScriptWrapper` object.
    
    :param sharedZennium: Zennium object.
    :type sharedZennium: :class:`~thales_remote.script_wrapper.ThalesRemoteScriptWrapper`
    :param epcChannel: Number of the EPC channel to which the device is connected via EPC cable.
        If a Rmux card is plugged in then the numbers have an offset.
    :param serialNumber: Serial number of the external potentiostat.
    """
    
    zenniumMutex = threading.Lock()
    
    def __init__(self, sharedZennium, epcPotentiostatId, serialNumber):
        self.sharedZenniumInterface = sharedZennium
        self._epcId = epcPotentiostatId
        self._serialNumber = serialNumber
        self._isInEPC = True
        
        self._commandInterface = None
        self.scpiInterface = None
        return
    
    def isSharedZenniumAvailable(self):
        """ Check if the zennium is available.
        
        The method checks if the threading.lock for synchronizing access to the Zennium is available.
        
        :returns: True if the zennium is not locked and available.
        :rtype: bool
        """
        return EpcScpiHandler.zenniumMutex.locked() == False
        
    def acquireSharedZennium(self, blocking = True, timeout = -1):
        """ Check if the Zennium is available.
        
        Wrapper for the aquire method of the lock object.
        https://docs.python.org/3/library/threading.html#lock-objects
        The parameters and return values are simply passed through.
        
        :param blocking: When invoked with the blocking argument set to True (the default),
            block until the lock is unlocked, then set it to locked and return True.
        :param timeout: When invoked with the floating-point timeout argument set to a positive value,
            block for at most the number of seconds specified by timeout and as long as the lock cannot
            be acquired. A timeout argument of -1 specifies an unbounded wait. It is forbidden to
            specify a timeout when blocking is false.
        :returns: The return value is True if the lock is acquired successfully, False if not
            (for example if the timeout expired).
        :rtype: bool
        """
        return EpcScpiHandler.zenniumMutex.acquire(blocking, timeout)
        
        
    def releaseSharedZennium(self):
        """ Release the Zennium object.
        
        Wrapper for the release method of the lock object.
        https://docs.python.org/3/library/threading.html#lock-objects
        
        Release a lock. This can be called from any thread, not only the thread which has acquired the lock.
        When the lock is locked, reset it to unlocked, and return. If any other threads are blocked
        waiting for the lock to become unlocked, allow exactly one of them to proceed.

        When invoked on an unlocked lock, a RuntimeError is raised.
        """
        EpcScpiHandler.zenniumMutex.release()
        return
    
    def connectSCPIDevice(self):
        """ Establish connection to the potentiostat.
        
        This method establishes the connection to the potentiostat (PP2x2, XPOT2) and passes it to the internal data structure.
        When invoked on an unlocked lock, a RuntimeError is raised.
        """
        deviceSearcher = SCPIDeviceSearcher()
        deviceSearcher.searchZahnerDevices()
        commandSerial, dataSerial = deviceSearcher.selectDevice(str(self._serialNumber))
        self._commandInterface = SerialCommandInterface(commandSerial)
        
        self.scpiInterface = SCPIDevice(self._commandInterface, SerialDataInterface(dataSerial))
        return
    
    def switchToSCPIAndReleaseSharedZennium(self):
        """ Switch from EPC to SCPI mode of the potentiostat and release the Zennium.
        
        The switch from EPC to SCPI must be made from the EPC operation, both control options can
        only release control but cannot take control away from each other.
        
        After the control is released, the Zennium is released.
        """
        self.sharedZenniumInterface.selectPotentiostat(self._epcId)
        
        self.sharedZenniumInterface.switchToSCPIControl()
        
        self._isInEPC = False
        self.releaseSharedZennium()
        """
        Wait a while until the USB connection is recognized by the operating system.
        """
        time.sleep(2)
        self.connectSCPIDevice()
        return
    
    def switchToSCPI(self):
        """ Switch from EPC to SCPI mode.
        
        It is recommended to use switchToSCPIAndReleaseSharedZennium() instead of this function.

        Before calling this method, the Zennium must have been released, since these methods call
        aquire and release themselves.
        If the zennium was locked bevore this function will block.
        """
        self.acquireSharedZennium()
        
        self.sharedZenniumInterface.selectPotentiostat(self._epcId)
        self.sharedZenniumInterface.switchToSCPIControl()
        
        self._isInEPC = False
        self.releaseSharedZennium()
        """
        Wait a little so that windows recognizes the new usb device when the potentiostat logs on again.
        """
        time.sleep(2)
        self.connectSCPIDevice()
        return
    
    def switchToEPC(self):
        """ Switch from SCPI to EPC mode.
        
        Before calling this method the Zennium must be locked with aquire.

        This method is used to switch from SCPI to EPC operation. After this method is called, the
        scpiInterface object is destroyed because the USB connection is closed.

        This method automatically selects the correct EPC channel.
        """
        try:
            self.scpiInterface.switchToEPCControl()
            self.scpiInterface.close()
        except:
            pass
        finally:
            self.scpiInterface = None
            self._isInEPC = True
            
        """
        Wait a little for the change to EPC.
        """
        time.sleep(2)
        self.sharedZenniumInterface.selectPotentiostat(self._epcId)
        return
        
    def close(self):
        """ Close the SCPI connection.
        
        The function is not required in epc mode.
        """
        if self._isInEPC == False:
            self.scpiInterface.close()
    
    
    
    