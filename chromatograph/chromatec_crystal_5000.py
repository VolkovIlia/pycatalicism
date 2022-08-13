import time

import pycatalicism.chromatograph.chromatograph_logging as chromatograph_logging
from pycatalicism.chromatograph.chromatec_control_panel_modbus import ChromatecControlPanelModbus
from pycatalicism.chromatograph.chromatec_control_panel_modbus import ConnectionStatus
from pycatalicism.chromatograph.chromatec_control_panel_modbus import WorkingStatus
from pycatalicism.chromatograph.chromatec_control_panel_modbus import ChromatographCommand
from pycatalicism.chromatograph.chromatec_control_panel_modbus import ApplicationCommand
from pycatalicism.chromatograph.chromatec_analytic_modbus import ChromatecAnalyticModbus
from pycatalicism.chromatograph.chromatograph_exceptions import ChromatographException
from pycatalicism.chromatograph.chromatograph_exceptions import ChromatographStateException

class ChromatecCrystal5000():
    """
    """

    def __init__(self, control_panel:ChromatecControlPanelModbus, analytic:ChromatecAnalyticModbus, methods:dict[str, int]):
        """
        """
        self._control_panel = control_panel
        self._analytic = analytic
        self._methods = methods
        self._logger = chromatograph_logging.get_logger(self.__class__.__name__)
        self._connection_status = self._control_panel.get_connection_status()
        self._working_status = self._control_panel.get_current_working_status()

    def connect(self):
        """
        Connect to chromatograph. If chromatec control panel is not up, start control panel, connection is established automatically in this case. If control panel is up, but chromatograph is disconnected, establish connection. Do nothing otherwise.

        raises
        ------
        ChromatographException
            if unknown connection status was get from chromatograph
        """
        self._connection_status = self._control_panel.get_connection_status()
        self._working_status = self._control_panel.get_current_working_status()
        if self._connection_status is ConnectionStatus.CP_OFF_NOT_CONNECTED:
            self._logger.info('Starting control panel application')
            self._control_panel.send_application_command(ApplicationCommand.START_CONTROL_PANEL)
            self._logger.info('Waiting until control panel is up...')
            while True:
                self._connection_status = self._control_panel.get_connection_status()
                self._logger.debug(f'{self._connection_status = }')
                if self._connection_status is ConnectionStatus.CP_ON_CONNECTED:
                    break
                time.sleep(1)
            self._logger.info('Control panel is UP. Connection established.')
        elif self._connection_status is ConnectionStatus.CP_ON_NOT_CONNECTED:
            self._logger.info('Connecting to chromatograph')
            self._control_panel.send_chromatograph_command(ChromatographCommand.CONNECT_CHROMATOGRAPH)
            self._logger.info('Waiting until connection is established...')
            while True:
                self._connection_status = self._control_panel.get_connection_status()
                self._logger.debug(f'{self._connection_status = }')
                if self._connection_status is ConnectionStatus.CP_ON_CONNECTED:
                    break
                time.sleep(1)
            self._logger.info('Connection established')
        elif self._connection_status is ConnectionStatus.CP_ON_CONNECTED:
            self._logger.info('Chromatograph connected already')
        else:
            raise ChromatographException(f'Unknown connection status: {self._connection_status}')
        self._working_status = self._control_panel.get_current_working_status()

    def set_method(self, method:str):
        """
        Set chromatograph instrument method. Chromatograph start to prepare itself for analysis accordingly.

        parameters
        ----------
        method:str
            method to send to chromatograph

        raises
        ------
        ChromatographStateException
            if connection to chromatograph is not established or analysis is in progress now
        """
        self._connection_status = self._control_panel.get_connection_status()
        self._working_status = self._control_panel.get_current_working_status()
        if self._connection_status is not ConnectionStatus.CP_ON_CONNECTED:
            raise ChromatographStateException('Connect to chromatograph first!')
        if self._working_status is WorkingStatus.ANALYSIS:
            raise ChromatographStateException('Analysis is in progress!')
        self._logger.info(f'Setting method to {method}')
        self._control_panel.set_instrument_method(self._methods[method])

    def is_ready_for_analysis(self) -> bool:
        """
        Check if chromatograph is ready for analysis.

        returns
        -------
        is_ready_for_analysis:bool
            True if chromatograph is ready for analysis

        raises
        ------
        ChromatographStateException
            if connection to chromatograph is not established
        """
        self._connection_status = self._control_panel.get_connection_status()
        self._working_status = self._control_panel.get_current_working_status()
        if self._connection_status is not ConnectionStatus.CP_ON_CONNECTED:
            raise ChromatographStateException('Connect to chromatograph first!')
        self._logger.info('Checking if chromatograph is ready for analysis')
        is_ready_for_analysis = self._working_status is WorkingStatus.READY_FOR_ANALYSIS
        self._logger.info(f'Chromatograph is ready for analysis: {is_ready_for_analysis}')
        return is_ready_for_analysis

    def start_analysis(self):
        """
        """
        raise NotImplementedError()

    def set_passport(self):
        """
        """
        raise NotImplementedError()
