#!/usr/bin/python3

import time

import RPi.GPIO as GPIO

def _read_spi_chunk(spi, reg, len):
	txn = [ reg | 0x80 ] + [ 0xff ] * len

	resp = spi.xfer2(txn)
	#print(resp)

	return resp[1:]

def _read_spi_reg(spi, reg):
	resp = _read_spi_chunk(spi, reg, 1)
	return resp[0]

def _write_spi_reg(spi, reg, val):
	#print("reg %x = %x"%(reg, val))
	spi.xfer2([reg, val])

def _assert_spi_reg(spi, reg, expected):
	val = _read_spi_reg(spi, reg)
	if (val == expected):
		return

	print("val %x vs %x"%(val, expected))
	raise RuntimeError("Did not get expected assert value")

def _repack_samples(l, scale):
	outp = []
	for i in range(0, len(l), 2):
		val = (l[i] & 0xf0) + (l[i+1] << 8)
		if (val >= 32768):
			val -= 65536

		outp.append(val / 32768.0 * scale)

	return tuple(outp)

def make_csvline(*args):
	line = ''

	for elem in args:
		for member in elem:
			if line:
				line += ','

			line += '%+08.2f'%member

	return line

class BMX055:
	"""
	This is a class that handles communications between a Raspberry Pi and
	a BMX055 sensor (accelerometer+gyro) attached via SPI.
	"""
	BMX055_REG_ACC_CHIPID=0x00
	BMX055_VAL_ACC_CHIPID=0xfa
	BMX055_REG_ACC_X_LSB=0x02
	BMX055_REG_ACC_X_MSB=0x03
	BMX055_REG_ACC_Y_LSB=0x04
	BMX055_REG_ACC_Y_MSB=0x05
	BMX055_REG_ACC_Z_LSB=0x06
	BMX055_REG_ACC_Z_MSB=0x07
	BMX055_REG_ACC_TEMP=0x08
	BMX055_ACC_TEMP_OFFSET=23
	BMX055_REG_ACC_INT_STATUS_0=0x09
	BMX055_REG_ACC_INT_STATUS_1=0x0a
	BMX055_REG_ACC_INT_STATUS_2=0x0b
	BMX055_REG_ACC_INT_STATUS_3=0x0c
	BMX055_REG_ACC_FIFO_STATUS=0x0e
	BMX055_REG_ACC_PMU_RANGE=0x0f
	BMX055_VAL_ACC_PMU_RANGE_2G=0x03
	BMX055_VAL_ACC_PMU_RANGE_4G=0x05
	BMX055_VAL_ACC_PMU_RANGE_8G=0x08
	BMX055_VAL_ACC_PMU_RANGE_16G=0x0c
	BMX055_REG_ACC_PMU_BW=0x10
	BMX055_VAL_ACC_PMU_BW_7HZ81=0x08
	BMX055_VAL_ACC_PMU_BW_15HZ63=0x09
	BMX055_VAL_ACC_PMU_BW_31HZ25=0x0a
	BMX055_VAL_ACC_PMU_BW_62HZ5=0x0b
	BMX055_VAL_ACC_PMU_BW_125HZ=0x0c
	BMX055_VAL_ACC_PMU_BW_250HZ=0x0d
	BMX055_VAL_ACC_PMU_BW_500HZ=0x0e
	BMX055_VAL_ACC_PMU_BW_1KHZ=0x0f
	BMX055_REG_ACC_PMU_LPW=0x11
	BMX055_VAL_ACC_PMU_LPW_NORMAL=0x00
	BMX055_REG_ACC_PMU_LOW_POWER=0x12
	BMX055_REG_ACC_ACCD_HBW=0x13
	BMX055_VAL_ACC_ACCD_HBW_NORMAL=0x00 #filtered data/shadowed
	BMX055_REG_ACC_BGW_SOFTRESET=0x14
	BMX055_VAL_ACC_BGW_SOFTRESET_REQ=0xb6 #value to trigger rest, 3ms delay required after
	BMX055_REG_ACC_INT_EN_0=0x16
	BMX055_REG_ACC_INT_EN_1=0x17
	BMX055_REG_ACC_INT_EN_2=0x18
	BMX055_REG_ACC_INT_MAP_0=0x19
	BMX055_REG_ACC_INT_MAP_1=0x1a
	BMX055_REG_ACC_INT_MAP_2=0x1b
	BMX055_REG_ACC_INT_SRC=0x1e
	BMX055_REG_ACC_INT_OUT_CTRL=0x20
	BMX055_REG_ACC_INT_RST_LATCH=0x21
	BMX055_REG_ACC_INT_0=0x22
	BMX055_REG_ACC_INT_1=0x23
	BMX055_REG_ACC_INT_2=0x24
	BMX055_REG_ACC_INT_3=0x25
	BMX055_REG_ACC_INT_4=0x26
	BMX055_REG_ACC_INT_5=0x27
	BMX055_REG_ACC_INT_6=0x28
	BMX055_REG_ACC_INT_7=0x29
	BMX055_REG_ACC_INT_8=0x2a
	BMX055_REG_ACC_INT_9=0x2b
	BMX055_REG_ACC_INT_A=0x2c
	BMX055_REG_ACC_INT_B=0x2d
	BMX055_REG_ACC_INT_C=0x2e
	BMX055_REG_ACC_INT_D=0x2f
	BMX055_REG_ACC_FIFO_CONFIG_0=0x30
	BMX055_REG_ACC_PMU_SELF_TEST=0x32
	BMX055_REG_ACC_TRIM_NVM_CTRL=0x33
	BMX055_REG_ACC_BGW_SPI3_WDT=0x34
	BMX055_REG_ACC_OFC_CTRL=0x36
	BMX055_REG_ACC_OFC_SETTING=0x37
	BMX055_REG_ACC_OFC_OFFSET_X=0x38
	BMX055_REG_ACC_OFC_OFFSET_Y=0x39
	BMX055_REG_ACC_OFC_OFFSET_Z=0x3a
	BMX055_REG_ACC_TRIM_GP0=0x3b
	BMX055_REG_ACC_TRIM_GP1=0x3c
	BMX055_REG_ACC_FIFO_CONFIG_1=0x3e
	BMX055_VAL_ACC_FIFO_CONFIG_1_BYPASS=0x00
	BMX055_REG_ACC_FIFO_DATA=0x3f

	BMX055_REG_GYRO_CHIPID=0x00
	BMX055_VAL_GYRO_CHIPID=0x0f
	BMX055_REG_GYRO_X_LSB=0x02
	BMX055_REG_GYRO_X_MSB=0x03
	BMX055_REG_GYRO_Y_LSB=0x04
	BMX055_REG_GYRO_Y_MSB=0x05
	BMX055_REG_GYRO_Z_LSB=0x06
	BMX055_REG_GYRO_Z_MSB=0x07
	BMX055_REG_GYRO_INT_STATUS_0=0x09
	BMX055_REG_GYRO_INT_STATUS_1=0x0A
	BMX055_REG_GYRO_INT_STATUS_2=0x0B
	BMX055_REG_GYRO_INT_STATUS_3=0x0C
	BMX055_REG_GYRO_FIFO_STATUS=0x0E
	BMX055_REG_GYRO_RANGE=0x0F
	BMX055_VAL_GYRO_RANGE_2000DPS=0x00
	BMX055_VAL_GYRO_RANGE_1000DPS=0x01
	BMX055_VAL_GYRO_RANGE_500DPS=0x02
	BMX055_VAL_GYRO_RANGE_250DPS=0x03
	BMX055_VAL_GYRO_RANGE_125DPS=0x04
	BMX055_REG_GYRO_BW=0x10
	BMX055_VAL_GYRO_BW_32HZ=0x07    # 100Hz ODR
	BMX055_VAL_GYRO_BW_64HZ=0x06    # 200Hz ODR
	BMX055_VAL_GYRO_BW_47HZ=0x03	#/*=400Hz=ODR=*/
	BMX055_VAL_GYRO_BW_116HZ=0x02	#/*=1KHz=ODR=*/
	BMX055_VAL_GYRO_BW_230HZ=0x01	#/*=2KHz=ODR=*/
	BMX055_VAL_GYRO_BW_UNFILT=0x00	#/*=2KHz=ODR=*/
	BMX055_REG_GYRO_LPM1=0x11
	BMX055_REG_GYRO_LPM2=0x12
	BMX055_REG_GYRO_RATE_HBW=0x13
	BMX055_REG_GYRO_BGW_SOFTRESET=0x14
	BMX055_VAL_GYRO_BGW_SOFTRESET_REQ=0xb6	#/*=Takes=30ms!=Typical!=*/
	BMX055_REG_GYRO_INT_EN_0=0x15
	BMX055_REG_GYRO_INT_EN_1=0x16
	BMX055_REG_GYRO_INT_MAP_0=0x17
	BMX055_REG_GYRO_INT_MAP_1=0x18
	BMX055_REG_GYRO_INT_MAP_2=0x19
	BMX055_REG_GYRO_INTERRUPTS_SELECTABLE_DATA_SOURCE=0x1A
	BMX055_REG_GYRO_FAST_OFFSET_COMPENSATION_MOTION_THRESHOLD=0x1B
	BMX055_REG_GYRO_MOTION_INT=0x1C
	BMX055_REG_GYRO_FIFO_WM_INT=0x1E
	BMX055_REG_GYRO_INT_RST_LATCH=0x21
	BMX055_REG_GYRO_HIGH_TH_X=0x22
	BMX055_REG_GYRO_HIGH_DUR_X=0x23
	BMX055_REG_GYRO_HIGH_TH_Y=0x24
	BMX055_REG_GYRO_HIGH_DUR_Y=0x25
	BMX055_REG_GYRO_HIGH_TH_Z=0x26
	BMX055_REG_GYRO_HIGH_DUR_Z=0x27
	BMX055_REG_GYRO_SOC=0x31
	BMX055_REG_GYRO_A_FOC=0x32
	BMX055_REG_GYRO_TRIM_NVM_CTRL=0x33
	BMX055_REG_GYRO_BGW_SPI3_WDT=0x34
	BMX055_REG_GYRO_OFC1=0x36
	BMX055_REG_GYRO_OFC2=0x37
	BMX055_REG_GYRO_OFC3=0x38
	BMX055_REG_GYRO_OFC4=0x39
	BMX055_REG_GYRO_TRIM_GP0=0x3A
	BMX055_REG_GYRO_TRIM_GP1=0x3B
	BMX055_REG_GYRO_BIST=0x3C
	BMX055_REG_GYRO_FIFO_CONFIG_0=0x3D
	BMX055_REG_GYRO_FIFO_CONFIG_1=0x3E
	BMX055_REG_GYRO_FIFO_DATA=0x3F

	def __init__(self, gyro_bus, gyro_instance, accel_bus, accel_instance,
			irq_pin):
		"""
		Instantiates class to communicate with BMX055 gyro.

		Parameters:
		    gyro_bus: The SPI bus that the gyro is on (probably 0).
		    gyro_instance: The SPI chip select that is used for the gyro.
		    accel_bus: The SPI bus that the accelerometer is on (probably 0).
		    accel_instance: The SPI chip select that is used for the accelerometer.
		    irq_pin: The Pi pin that is connected to INT3 on the gyro.
		"""

		import spidev

		self.spi_gyro = spidev.SpiDev()
		self.spi_accel = spidev.SpiDev()
		self.irq_pin = irq_pin

		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(irq_pin, GPIO.IN)

		self.spi_gyro.open(gyro_bus, gyro_instance)
		self.spi_accel.open(accel_bus, accel_instance)

		self.spi_gyro.max_speed_hz = 10000000
		self.spi_accel.max_speed_hz = 10000000

		# Verify chip IDs
		self.__assert_spigyro_reg(self.BMX055_REG_GYRO_CHIPID, self.BMX055_VAL_GYRO_CHIPID)
		self.__assert_spiaccel_reg(self.BMX055_REG_ACC_CHIPID, self.BMX055_VAL_ACC_CHIPID)

		# trigger a reset sequence
		self.__write_spigyro_reg(self.BMX055_REG_GYRO_BGW_SOFTRESET, self.BMX055_VAL_GYRO_BGW_SOFTRESET_REQ)
		self.__write_spiaccel_reg(self.BMX055_REG_ACC_BGW_SOFTRESET, self.BMX055_VAL_ACC_BGW_SOFTRESET_REQ)

		# Wait a long time, since the gyro portion is slow
		time.sleep(0.10)

		# Verify chip IDs again
		self.__assert_spigyro_reg(self.BMX055_REG_GYRO_CHIPID, self.BMX055_VAL_GYRO_CHIPID)
		self.__assert_spiaccel_reg(self.BMX055_REG_ACC_CHIPID, self.BMX055_VAL_ACC_CHIPID)

		# Program bandwidths / ODR.
		# We read relative to the gyro, which means that we may duplicate accel samples
		# due to jitter This will cause some intermodulation, etc, of accel, but
		# shouldn't be too bad. (self.because the gyro/accel are async)

		# Corresponds to 250Hz ODR, which means we miss some points and will have
		# some nasty mixer products
		self.__write_spiaccel_reg(self.BMX055_REG_ACC_PMU_BW, self.BMX055_VAL_ACC_PMU_BW_125HZ)

		# Get data at 200Hz
		self.__write_spigyro_reg(self.BMX055_REG_GYRO_BW, self.BMX055_VAL_GYRO_BW_64HZ)

		# Program ranges
		self.__write_spiaccel_reg(self.BMX055_REG_ACC_PMU_RANGE, self.BMX055_VAL_ACC_PMU_RANGE_16G)
		self.__write_spigyro_reg(self.BMX055_REG_GYRO_RANGE, self.BMX055_VAL_GYRO_RANGE_2000DPS)

		# Program interrupts
		self.__write_spigyro_reg(self.BMX055_REG_GYRO_INT_EN_0, 0x80) # enable new data int
		self.__write_spigyro_reg(self.BMX055_REG_GYRO_INT_EN_1, 0) # Interrupts active low, push-pull
		self.__write_spigyro_reg(self.BMX055_REG_GYRO_INT_MAP_1, 1) # Map new data interrupt to INT3 pin

		# Ignore the first few samples because they are garbage (filters initializing)
		for i in range(5):
			self.get_sample()


	def __write_spigyro_reg(self, reg, val):
		_write_spi_reg(self.spi_gyro, reg, val)

	def __write_spiaccel_reg(self, reg, val):
		_write_spi_reg(self.spi_accel, reg, val)

	def __assert_spigyro_reg(self, reg, expected):
		_assert_spi_reg(self.spi_gyro, reg, expected)

	def __assert_spiaccel_reg(self, reg, expected):
		_assert_spi_reg(self.spi_accel, reg, expected)

	def get_sample(self):
		"""
		This waits for the gyro interrupt line, and then reads from the
		accelerometer and gyro the most recent measurements.

		It returns a tuple, containing a tuple containing the current time,
		a tuple containing the P, Q, R rotation rate measurements, and a tuple containing
		the X, Y, and Z accelerations.

		e.g. 
		((1576093685.1627932,), (-0.9765625, 0.0, -0.9765625), (0.3828125, 0.22968750000000002, 10.029687500000001))
 
		"""

		count = 0
		while (GPIO.input(self.irq_pin) == True):
			count = count + 1

		#print(count)

		gyro_samples = _read_spi_chunk(self.spi_gyro, self.BMX055_REG_GYRO_X_LSB, 6)
		accel_samples = _read_spi_chunk(self.spi_accel, self.BMX055_REG_ACC_X_LSB, 6)

		gyro_converted = _repack_samples(gyro_samples, 2000)
		accel_converted = _repack_samples(accel_samples, 16*9.8)

		while (GPIO.input(self.irq_pin) == False):
			pass

		return ((time.time(),), gyro_converted, accel_converted)


if __name__ == "__main__":
	bmx = BMX055(0, 1, 0, 2, 32)

	samples = 0

	sample = bmx.get_sample()
	print(make_csvline(*sample))
