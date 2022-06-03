import serial

from pycatalicism.furnace.controller import Controller
from pycatalicism.furnace.furnace_data import FurnaceData
from pycatalicism.furnace.furnace_exception import FurnaceException

class Owen_TPM101_Controller(Controller):
    """
    """

    def __init__(self, port:str, baudrate:int, bytesize:int, parity:str, stopbits:float, timeout:float, write_timeout:float, rtscts:bool, address:int, rsdl:int, address_len:int):
        """
        """
        super().__init__(port=port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout, write_timeout=write_timeout, rtscts=rtscts)
        self.address = address
        self.rsdl = rsdl
        self.address_len = address_len #NB: only 8b adress supported

    def heat(self, temperature:int, wait:int|None) -> FurnaceData:
        """
        """
        raise NotImplementedError()

    def _handshake(self) -> bool:
        """
        """
        command = 'dev'
        message = self._prepare_request(command)
        response = self._get_response(message)
        device_name = self._get_device_name(response)
        return device_name == 'ТРМ101' #NB: <- this is utf-8 string written in russian, so ascii answer can be different, check ASCII codes!!!

    def _prepare_request(self, command:str) -> str:
        """
        """
        command_id = self._get_command_id(command)
        command_hash = self._get_command_hash(command_id)
        message_ascii = self._get_message_ascii(address=self.address, request=True, data_length=0, command_hash=command_hash, data=None)
        return message_ascii

    def _get_response(self, message:str) -> str:
        """
        """
        self._write_message(message)
        receipt = self._read_message(read_timeout=50)
        if not self._receipt_is_ok(receipt, message):
            raise FurnaceException(f'Got wrong receipt from device!')
        response = self._read_message(read_timeout=0)
        return response

    def _get_device_name(self, response:str) -> str:
        """
        """
        _, address, flag_byte, response_hash, data, crc = self._unpack_message(response)
        if not self._crc_is_ok(address, flag_byte, response_hash, data, crc):
            raise FurnaceException(f'Wrong CRC in response message!')
        device_name = self._decrypt_string(data)
        return device_name

    def _get_command_id(self, command:str) -> list[int]:
        """
        """
        raise NotImplementedError()

    def _get_command_hash(self, command_id:list[int]) -> int:
        """
        """
        raise NotImplementedError()

    def _get_message_ascii(self, address:int, request:bool, data_length:int, command_hash:int, data:None) -> str:
        """
        """
        raise NotImplementedError()

    def _write_message(self, message:str):
        """
        """
        raise NotImplementedError()

    def _read_message(self, read_timeout) -> str:
        """
        """
        raise NotImplementedError()

    def _receipt_is_ok(self, receipt:str, message:str) -> bool:
        """
        """
        raise NotImplementedError()
