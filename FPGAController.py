from IGPIOController import IGPIOController
from ctypes import *
from dwfconstants import *
import sys
import time

class DIO:
    acertou = (13)
    errou = (14)
    timeout = (15)
    mostrando = (12)
    dificuldade = (7)
    reset = (1)
    clock = (0)
    start = (6)
    dificuldade = (7)
    leds = (11, 8)
    chaves = [2,3,4,5]


class FPGAController(IGPIOController):
    """Mocking real implementation for FPGA communication."""

    def __init__(self):
        if sys.platform.startswith("win"):
            self.dwf = cdll.dwf
        elif sys.platform.startswith("darwin"):
            self.dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
        else:
            self.dwf = cdll.LoadLibrary("libdwf.so")
        self.hdwf = c_int()
        self.dwRead = c_uint32()
        self.hzSys = c_double()
        self.gpio_state = [0 for _ in range(32)]
        self.initial_setup()
        self.setup_clock()
        self.update_gpio_status()
    
    # Opens device and configures GPIOs for writing
    def initial_setup(self):
        self.dwf.FDwfDeviceOpen(c_int(-1), byref(self.hdwf))
        if self.hdwf.value == hdwfNone.value:
            print("[WAVEFORMS] failed to open device")
            szerr = create_string_buffer(512)
            self.dwf.FDwfGetLastErrorMsg(szerr)
            print(str(szerr.value))
            quit()
        else: 
            print("Initialized")
        self.dwf.FDwfDigitalOutInternalClockInfo(self.hdwf, byref(self.hzSys))
        self.dwf.FDwfDigitalIOConfigure(self.hdwf)
        # Only reset, chaves and start can be written to, the rest is read
        self.dwf.FDwfDigitalIOOutputEnableSet(self.hdwf, c_int(0b1111110))

    def setup_clock(self):
        # 1kHz pulse on DIO-0
        self.dwf.FDwfDigitalOutEnableSet(self.hdwf, c_int(0), c_int(1))
        print(self.hzSys)
        self.dwf.FDwfDigitalOutDividerSet(self.hdwf, c_int(0), c_int(int(self.hzSys.value/1e3)))
        self.dwf.FDwfDigitalOutCounterSet(self.hdwf, c_int(0), c_int(1), c_int(1))
        self.dwf.FDwfDigitalOutConfigure(self.hdwf, c_int(1))

    def isDisplayActive(self) -> bool:
        return bool(self.gpio_state[DIO.mostrando])
        
    def readLedSignal(self) -> int:
        # This indexes from 11 to 8 - 1 and reverses the list for us so that led 0 is at index 0
        return self.gpio_state[DIO.leds[0] : DIO.leds[1] - 1 : -1]
    
    def writeLedSignal(self, led_signal) -> None:
        # led_signal is actually the chave being pressed

        self.trigger_chave(led_signal)

    def write_gpio(self, channel, value):
        # If you don't do this, the clock will stop at high
        self.dwRead.value &= ~1  # This clears the LSB (sets it to 0)

        if value:
            self.dwRead.value |= (1 << channel)  # Set the bit for this channel
        else:
            self.dwRead.value &= ~ (1 << channel)  # Clear the bit for this channel

        self.dwf.FDwfDigitalIOOutputSet(self.hdwf, self.dwRead.value)

    # TODO isso daqui não tá funcionando corretamente. 
    def trigger_chave(self, chave):
        
        self.write_gpio(chave + 2, 1)
        time.sleep(.1)
        self.write_gpio(chave + 2, 0)

    def triggerStart(self) -> None:
        self.write_gpio(DIO.start, 1)
        time.sleep(.1)
        self.write_gpio(DIO.start, 0)

    def triggerReset(self) -> None:
        self.write_gpio(DIO.reset, 1)
        time.sleep(.1)
        self.write_gpio(DIO.reset, 0)

    def checkWinCondition(self) -> bool:
        self.update_gpio_status()
        return self.gpio_state[DIO.acertou]
    
    def checkLoseCondition(self) -> bool:
        self.update_gpio_status()
        return bool(self.gpio_state[DIO.errou] or self.gpio_state[DIO.timeout])
    
    def update_gpio_status(self):
        # fetch digital IO information from the device 
        self.dwf.FDwfDigitalIOStatus(self.hdwf) 
        # read state of all pins, regardless of output enable
        self.dwf.FDwfDigitalIOInputStatus(self.hdwf, byref(self.dwRead)) 
        self.gpio_state = [int(i) for i in reversed(bin(self.dwRead.value)[2:].zfill(16))]
    
    def close_device(self):
        self.dwf.FDwfDeviceClose(self.hdwf)
