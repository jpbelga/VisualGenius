from IGPIOController import IGPIOController

class FPGAController(IGPIOController):
    """Mocking real implementation for FPGA communication."""

    def isDisplayActive(self) -> bool:
        # Real GPIO interaction here
        return True  # Example placeholder

    def readLedSignal(self) -> int:
        # Read actual GPIO input
        return 0b1001  

    def writeLedSignal(self, led_signal: int) -> None:
        # Send data to FPGA
        print(f"Writing {led_signal:04b} to FPGA")

    def triggerStart(self) -> None:
        # Send start signal
        print("Starting FPGA process...")

    def triggerReset(self) -> None:
        # Send start signal
        print("Starting FPGA process...")

    def checkWinCondition(self) -> bool:
        # Check FPGA response
        return True  

    def checkLoseCondition(self) -> bool:
        # Check FPGA response
        return False  
