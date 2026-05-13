from typing import Any, Dict

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
    
    def allocate(self, value: Any) -> int:
        """Allocate a new cell in the store with the given value and return its address."""
        vvvprint(f"Store: Allocating new cell with value {value} at location {self.next_location}...")
        loc = self.next_location
        self.memory[loc] = Cell(value)
        self.next_location += 1
        vvvprint(f"Store: Cell allocated at location {loc}.")
        return loc
    
    def get(self, address: int) -> Any:
        vvvprint(f"Store: Retrieving value at address {address}...")
        if address not in self.memory:
            raise Exception(f"Address {address} not found in store.")
        vvvprint(f"Store: Value at address {address}: {self.memory[address].value}")
        return self.memory[address].value

    def set(self, address: int, value: Cell):
        vvvprint(f"Store: Setting value at address {address}...")
        if address not in self.memory:
            raise Exception(f"Address {address} not found in store.")
        self.memory[address].value = value
        vvvprint(f"Store: Value at address {address} set to {value}.")
