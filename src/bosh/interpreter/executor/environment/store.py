from typing import Any, Dict
from bosh.helper_functions.logged import logged, LogCase

class Cell:
    def __init__(
            self,
            value: Any, 
        ):
        self.value = value

class Store:
    def __init__(self):
        self.memory: Dict[int, Cell] = {}
        self.next_location: int = 0
    
    
    @logged(
        start=lambda self, value: (
            f"Attempting to allocate new cell with value {value} in store..."
        ),
        success={
            "success": lambda self, value, loc: (
                f"New cell with value {value} allocated in store at location {loc}, in store, successfully."
            )
        }
    )
    def allocate(self, value: Any, log_case: LogCase) -> int:
        """Allocate a new cell in the store with the given value and return its address."""
        loc = self.next_location
        self.memory[loc] = Cell(value)
        self.next_location += 1
        log_case.set("success", loc=loc)
        return loc


    @logged(
        start=lambda self, address: (
            f"Attempting to retrieve value at address {address} from store..."
        ),
        success={
            "success": lambda self, address, value: (
                f"Value {value} retrieved from store at address {address} successfully."
            )
        }
    )
    def get(self, address: int, log_case: LogCase) -> Any:
        if address not in self.memory:
            raise Exception(f"Address {address} not found in store.")
        value = self.memory[address].value
        log_case.set("success", value=value)
        return value

    
    @logged(
        start=lambda self, address, value: (
            f"Attempting to set value at address {address} in store to {value}..."
        ),        success={
            "success": lambda self, address, value: (
                f"Value at address {address} in store set to {value} successfully."
            )
        }
    )
    def set(self, address: int, value: Cell, log_case: LogCase):
        if address not in self.memory:
            raise Exception(f"Address {address} not found in store.")
        self.memory[address].value = value
        log_case.set("success")
