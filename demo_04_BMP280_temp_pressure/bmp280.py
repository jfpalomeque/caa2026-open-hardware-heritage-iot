# bmp280.py - minimal BMP280 driver for MicroPython (I2C)
from micropython import const
import time

_REG_ID = const(0xD0)
_REG_RESET = const(0xE0)
_REG_STATUS = const(0xF3)
_REG_CTRL_MEAS = const(0xF4)
_REG_CONFIG = const(0xF5)
_REG_PRESS_MSB = const(0xF7)

_RESET_VALUE = const(0xB6)

class BMP280:
    def __init__(self, i2c, address=0x76):
        self.i2c = i2c
        self.address = address

        chip_id = self._read8(_REG_ID)
        if chip_id != 0x58:
            raise OSError("BMP280 not found (chip id: {})".format(hex(chip_id)))

        # Soft reset
        self._write8(_REG_RESET, _RESET_VALUE)
        time.sleep_ms(10)

        # Read calibration data
        self._read_calibration()

        # config: standby 1000ms (0b101), filter off (0), spi3w off
        self._write8(_REG_CONFIG, 0xA0)

        # ctrl_meas: temp oversampling x1, pressure oversampling x1, normal mode
        self._write8(_REG_CTRL_MEAS, 0x27)

        self.t_fine = 0

    def _read8(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def _write8(self, reg, val):
        self.i2c.writeto_mem(self.address, reg, bytes([val]))

    def _read_u16_le(self, reg):
        b = self.i2c.readfrom_mem(self.address, reg, 2)
        return b[0] | (b[1] << 8)

    def _read_s16_le(self, reg):
        v = self._read_u16_le(reg)
        return v - 65536 if v > 32767 else v

    def _read_calibration(self):
        # Calibration registers start at 0x88 and are 24 bytes for BMP280
        self.dig_T1 = self._read_u16_le(0x88)
        self.dig_T2 = self._read_s16_le(0x8A)
        self.dig_T3 = self._read_s16_le(0x8C)

        self.dig_P1 = self._read_u16_le(0x8E)
        self.dig_P2 = self._read_s16_le(0x90)
        self.dig_P3 = self._read_s16_le(0x92)
        self.dig_P4 = self._read_s16_le(0x94)
        self.dig_P5 = self._read_s16_le(0x96)
        self.dig_P6 = self._read_s16_le(0x98)
        self.dig_P7 = self._read_s16_le(0x9A)
        self.dig_P8 = self._read_s16_le(0x9C)
        self.dig_P9 = self._read_s16_le(0x9E)

    def _read_raw(self):
        # Wait if measuring
        while self._read8(_REG_STATUS) & 0x08:
            time.sleep_ms(2)

        data = self.i2c.readfrom_mem(self.address, _REG_PRESS_MSB, 6)
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        return adc_t, adc_p

    def temperature(self):
        adc_t, _ = self._read_raw()

        var1 = (((adc_t >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11
        var2 = (((((adc_t >> 4) - self.dig_T1) * ((adc_t >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        self.t_fine = var1 + var2
        t = (self.t_fine * 5 + 128) >> 8
        return t / 100.0

    def pressure(self):
        # Ensure t_fine updated
        _ = self.temperature()
        _, adc_p = self._read_raw()

        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = ((var1 * var1 * self.dig_P3) >> 8) + ((var1 * self.dig_P2) << 12)
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33

        if var1 == 0:
            return 0.0

        p = 1048576 - adc_p
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.dig_P8 * p) >> 19

        p = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
        return (p / 256.0) / 100.0  # hPa

    @property
    def values(self):
        t = self.temperature()
        p = self.pressure()
        return ("{:.2f}C".format(t), "{:.2f}hPa".format(p))