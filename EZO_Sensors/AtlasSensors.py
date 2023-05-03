import board, busio
import time


class i2cHelper(object):
    _i2c: busio.I2C

    def __init__(self, scl, sda, frequency):
        self._i2c = busio.I2C(scl, sda, frequency)
        while not self._i2c.try_lock():
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._i2c.unlock()

    def deinit(self):
        self._i2c.unlock()

    def _i2c_write(self, address: int, message: str,) -> None:
        self._i2c.writeto(address, message)

    def _i2c_write_read(
        self,
        address: int,
        message: str,
        waitTime: float,
        buf_size: int = 40,
        print_output: bool = False,
    ):
        self._i2c_write(address, message)
        result = bytearray(buf_size)
        time.sleep(waitTime)
        self._i2c.readfrom_into(address, result)
        if print_output == True:
            print(result.decode("utf-8"))
        return result

    def show_name(self, address: int) -> None:
        """Show the name of the i2c device with the specified address"""
        res = self._i2c_write_read(address, "Name,?", 0.3, 24)
        print("name:", res.decode("utf-8"))

    def identify_devices(self) -> None:
        """Display all devices in the system"""
        for address in self._i2c.scan():
            res = self._i2c_write_read(address, "i", 0.3, 13)
            print("Device information:", res.decode("utf-8"))
            self.show_name(address)
            print("i2c address:", address)


class generic_ezo(object):
    """Generic EZO class for reading from """

    _i2c: busio.I2C

    def __init__(self, address: int, i2c, print_res: bool = False) -> None:
        self._address = address
        self._print_res = print_res
        self._i2c = i2c

    def _i2c_write(self, address: int, message: str,) -> None:
        self._i2c.writeto(address, message)

    def _i2c_write_read(
        self,
        address: int,
        message: str,
        waitTime: float,
        buf_size: int = 40,
        print_output: bool = False,
    ):
        self._i2c_write(address, message)
        result = bytearray(buf_size)
        time.sleep(waitTime)
        self._i2c.readfrom_into(address, result)
        if print_output == True:
            print(result.decode("utf-8"))
        return result

    def read_bytearray(self) -> bytearray:
        """Reads the device, outputs as a byte array"""
        return self._i2c_write_read(self._address, "R", 0.9, 7, self._print_res)

    def read(self) -> float:
        """Reads the ORP, decodes to float"""
        result = self._i2c_write_read(self._address, "R", 0.9, 7, self._print_res)
        result1 = result[1:5]
        result_decode = float(result1.decode("utf-8"))
        return result_decode

    def sleep(self) -> None:
        self._i2c.writeto(self._address, "Sleep")

    def status_bytearray(self) -> bytearray:
        self._i2c.writeto(self._address, "Status")
        time.sleep(0.3)
        result = bytearray(17)
        self._i2c.readfrom_into(self._address, result)
        if self._print_res is True:
            print(result)
        return result


class ph_ezo(generic_ezo):

    DEFAULT_ADDRESS = 99

    def __init__(self, address: int, i2c, print_res: bool = False) -> None:
        super(ph_ezo, self).__init__((address or self.DEFAULT_ADDRESS), i2c, print_res)

    def calibrate(self, points="low") -> bytearray:
        result = bytearray(2)
        if points == "low":
            self._i2c.writeto(self._address, "Cal,low,4.00")
            time.sleep(0.9)
            self._i2c.readfrom_into(self._address, result)

        if points == "mid":
            self._i2c.writeto(self._address, "Cal,mid,7.00")
            time.sleep(0.9)
            self._i2c.readfrom_into(self._address, result)

        if points == "high":
            self._i2c.writeto(self._address, "Cal,high,10.00")
            time.sleep(0.9)
            self._i2c.readfrom_into(self._address, result)

        if self._print_res is True:
            print(result)
        return result
