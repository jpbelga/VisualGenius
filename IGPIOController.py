from abc import ABC, abstractmethod

class IGPIOController(ABC):
    """
    Interface for controlling GPIO signals of an FPGA for game-related operations.
    """

    @abstractmethod
    def isDisplayActive(self) -> bool:
        """
        Checks if the display is currently active.
        
        Returns:
            bool: True if the display is showing something, False otherwise.
        """
        pass

    @abstractmethod
    def readLedSignal(self) -> list[int]:
        """
        Reads the 4-bit LED signal from the FPGA.
        
        Returns:
            int: The current 4-bit LED signal.
        """
        pass

    @abstractmethod
    def writeLedSignal(self, led_signal: list[int]) -> None:
        """
        Sends a 4-bit LED signal to the FPGA.
        
        Args:
            led_signal (int): The 4-bit value to set the LED signal.
        """
        pass

    @abstractmethod
    def triggerStart(self) -> None:
        """
        Sends a command to start the game.
        """
        pass

    @abstractmethod
    def triggerReset(self) -> None:
        """
        Sends a command to reset the game.
        """
        pass

    @abstractmethod
    def checkWinCondition(self) -> bool:
        """
        Checks if the game has ended with a win.
        
        Returns:
            bool: True if the game was won, False otherwise.
        """
        pass

    @abstractmethod
    def checkLoseCondition(self) -> bool:
        """
        Checks if the game has ended with a loss.
        
        Returns:
            bool: True if the game was lost, False otherwise.
        """
        pass
