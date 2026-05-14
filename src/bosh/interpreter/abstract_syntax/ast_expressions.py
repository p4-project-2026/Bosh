from .ast_base import *

@dataclass
class NumberLiteral(ASTNode):
    value: float
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[set[str]]:
        return {"number"}
    
    def execute(self, env: Environment) -> float:
        return self.value
    
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # Number literals are only compatible with "number", "decimal", and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("NumberLiteral: inference: Number literals cannot be narrowed to type '{new_inference_value}'", self)


@dataclass
class DecimalLiteral(ASTNode):
    value: float
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[set[str]]:
        return {"decimal"}
    
    def execute(self, env: Environment) -> float:
        return self.value

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # Decimal literals are only compatible with "decimal" and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("DecimalLiteral: inference: Decimal literals cannot be narrowed to type '{new_inference_value}'", self)

@dataclass
class StringLiteral(ASTNode):
    value: str
    def  __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[set[str]]:
        return {"text"}

    def execute(self, env: Environment) -> str:
        return self.value

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # String literals are only compatible with "text" and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("StringLiteral: inference: String literals cannot be narrowed to type '{new_inference_value}'", self)

@dataclass
class InterpolatedString(ASTNode):
    parts: List[ASTNode]
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[set[str]]:
        for part in self.parts:
            if part.check(v_table, f_table) is None:
                raise BoshTypeError("Undefined variable in interpolated string", self)
        return {"text"}

    def execute(self, env: Environment) -> str:
        result = ""
        for part in self.parts:
            value = part.execute(env)
            result += str(value)
        return result
    
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # Interpolated strings are only compatible with "text" and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("InterpolatedString: inference: Interpolated string literals cannot be narrowed to type '{new_inference_value}'", self)
    
@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[set[str]]:
        return {"boolean"}

    def execute(self, env: Environment) -> bool:
        return self.value

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # Boolean literals are only compatible with "boolean" and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("BooleanLiteral: inference: Boolean literals cannot be narrowed to type '{new_inference_value}'", self)

@dataclass
class NullLiteral(ASTNode):
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[set[str]]:
        return {"null"}
    
    def execute(self, env: Environment) -> None:
        return None

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # Null literals are compatible with all types, so they can be narrowed to any type without error.
        pass

@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[set[str]]:
        if len(self.elements) == 0:
            return {"list<any>"}
        element_type = self.elements[0].check(v_table, f_table)
        for elem in self.elements[1:]:
            elem_type = elem.check(v_table, f_table)
            if elem_type != element_type:
                raise BoshTypeError(f"List elements must all be of the same type, expected {element_type}, got {elem_type}", self)
        return {f"list<{element_type}>"}

    def execute(self, env: Environment) -> List[Any]:
        return [elem.execute(env) for elem in self.elements]

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # List literals are only compatible with "list<elem_type>" and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("ListLiteral: inference: List literals cannot be narrowed to type '{new_inference_value}'", self)

@dataclass
class Identifier(ASTNode):
    name: str
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> set[str]:
        try:
            vvvprint(f"Identifier: check: Looking up variable '{self.name}' in variable table...")
            var_type = v_table.lookup(self.name)
            vvvprint(f"Identifier: check: Variable '{self.name}' found with type '{var_type}'")
        except Exception:
            raise BoshTypeError(f"Undefined variable '{self.name}'", self)
        self.value_node_pairs.append((var_type.copy(), self))
        return var_type

    def execute(self, env: Environment) -> Any:
        vvvprint(f"Identifier: execute: Looking up variable '{self.name}'...")
        try:
            vvvprint(f"Identifier: execute: Variable '{self.name}' found. Retrieving value...")
            value = env.lookup_variable(self.name)
            vvvprint(f"Identifier: execute: Value of variable '{self.name}': {value}")
        except Exception as e:
            raise 
        return value

    def inference(
        self,
        v_table: ScopeStack,
        f_table: FuncTable,
        old_inference_value: set[str],
        new_inference_value: set[str],
    ) -> None:
        
        if not self.value_node_pairs:
            raise Exception(f"Identifier: inference: No remembered type found for variable '{self.name}', '{self}' has not been checked.", self)
        remembered_type = self.value_node_pairs[0][0].copy()
        narrowed = remembered_type & old_inference_value
        if not narrowed:
            raise Exception(f"Identifier: inference: Cannot narrow variable '{self.name}' from type '{remembered_type}' to incompatible type '{new_inference_value}'.", self)
        narrowed = new_inference_value & remembered_type
        if not narrowed:
            raise Exception(f"Identifier: inference: Cannot narrow variable '{self.name}' from type '{remembered_type}' to incompatible type '{new_inference_value}'.", self)
        try:
            v_table.bind(self.name, narrowed.copy())
        except Exception as e:
            raise Exception(f"Identifier: inference: Error updating variable '{self.name}' in variable table during inference: {e}", self, cause=e)
        self.value_node_pairs[0] = (narrowed.copy(), self.value_node_pairs[0][1])
        return
        

@dataclass
class TaskCall(ASTNode):
    name: str
    arguments: Optional[List[ASTNode]] = None
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
            signature = f_table.lookup(self.name)
        except Exception:
            raise BoshTypeError(f"Undefined task '{self.name}'", self)
        
        if len(self.arguments) != len(signature.param_types):
            raise BoshTypeError(f"Task '{self.name}' expects {len(signature.param_types)} arguments, but {len(self.arguments)} were provided.", self)
        for i, arg in enumerate(self.arguments):
            if i < len(signature.param_types):
                arg_type = arg.check(v_table, f_table)
                expected_type = signature.param_types[signature.param[i]]
                if arg_type != expected_type and expected_type != "any":
                    raise BoshTypeError(f"Argument {i+1} of task '{self.name}' expects type '{expected_type}', but got '{arg_type}'.", self)
        return signature.return_type

    def execute(self, env: Environment) -> Any:
        try:
            vvvprint(f"Task Call: Looking up task '{self.name}'...")
            task_func = env.get_function(self.name)
            vvvprint(f"Task Call: Task '{self.name}' found: {task_func}")
        except Exception as e:
            raise BoshRuntimeError(f"Error executing task '{self.name}':", self, cause=e)
        
        values : List[Any] = []
        for i in range(len(task_func.parameters)):
            vvvprint(f"Task Call: Evaluating argument {i+1} for task '{self.name}'...")
            values.append(self.arguments[i].execute(env))
            vvvprint(f"Task Call: Argument {i+1} for task '{self.name}' evaluated to: {values[-1]}")
        
        env.enter_function_scope(self.name)
        for i in range(len(task_func.parameters)):
            param_name = task_func.parameters[i]
            param_value = values[i]
            vvvprint(f"Task Call: Binding parameter '{param_name}' to value '{param_value}' in function scope for task '{self.name}'...")
            env.assign_variable(param_name, param_value)
            vvvprint(f"Task Call: Parameter '{param_name}' bound to value '{param_value}' in function scope for task '{self.name}'.")
        try:
            vvvprint(f"Task Call: Executing body of task '{self.name}'...")
            result = task_func.body.execute(env)
            vvvprint(f"Task Call: Body of task '{self.name}' executed successfully. Result: {result}")
            return result
        except Exception as e:
            raise BoshRuntimeError(f"Error executing task '{self.name}':", self, cause=e)


@dataclass
class ListLookup(ASTNode):
    target: ASTNode
    index: ASTNode
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[set[str]]:
        target_types = self.target.check(v_table, f_table)
        index_type = self.index.check(v_table, f_table)
        vvvprint(f"ListLookup: Target types: {target_types}, Index type: {index_type}")
        if index_type != "number":
            vvvprint(f"ListLookup: Index type '{index_type}' is not 'number'.")
            if index_type == "UNKNOWN":
                vvvprint(f"ListLookup: Type Check: Index type is unknown. Attempting inference.")
                self.index.inference(v_table, f_table, index_type, {"number"})
                vvvprint(f"ListLookup: Type Check: After inference, index type is now 'number'.")
            else:
                raise Exception(f"ListLookup: List index must be of type 'number', got '{index_type}'", self)
        vvvprint(f"ListLookup: Checking if target types are compatible with list lookup...")
        return_types = set()
        for target_type in target_types:
            for target_type in target_types:
                if target_type.startswith("list<") and target_type.endswith(">"):
                    return_types.add(target_type[5:-1])
        if not return_types:
            raise Exception(f"ListLookup: Cannot index into type '{target_types}', expected a list type", self)
        vvvprint(f"ListLookup: Target types compatible with list lookup. Return types: {return_types}")
        self.value_node_pairs.append((return_types, self))

        return return_types
    
    def execute(self, env: Environment) -> Any:
        vvvprint(f"ListLookup: execute: Executing list lookup. Target: {self.target}, Index: {self.index}")
        try:
            vvvprint(f"ListLookup: execute: Evaluating target '{self.target}'...")
            target_value = self.target.execute(env)
        except Exception as e:
            raise BoshRuntimeError(f"Error executing list lookup: {e}", self)
        vvvprint(f"ListLookup: execute: Target evaluated successfully. Value: {target_value}")
        index_value = self.index.execute(env)
        vvvprint(f"ListLookup: execute: Index evaluated successfully. Value: {index_value}")
        try:
            vvvprint(f"ListLookup: execute: Attempting to index into target with index...")
            return target_value[int(index_value)]
        except Exception as e:
            raise BoshRuntimeError(f"Error executing list lookup: {e}", self)
        
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        vvvprint(f"ListLookup: inference: Starting inference for list lookup with old inference value '{old_inference_value}' and new inference value '{new_inference_value}'...")
        if not self.value_node_pairs:
            raise Exception("ListLookup: inference: No type information available for list lookup during type inference", self)
        vvvprint(f"ListLookup: Current value-node pairs: {self.value_node_pairs}")
    
        if old_inference_value != self.value_node_pairs[0][0]:
            vvvprint(f"ListLookup: inference: Old inference value '{old_inference_value}' does not match remembered type '{self.value_node_pairs[0][0]}'. No update performed.")
            if self.value_node_pairs[0][0].issubset(old_inference_value):
                vvvprint(f"ListLookup: inference: Remembered type '{self.value_node_pairs[0][0]}' is a subset of old inference value '{old_inference_value}'. No update performed.")
                if new_inference_value.issubset(self.value_node_pairs[0][0]):
                    vvvprint(f"ListLookup: inference: New inference value '{new_inference_value}' is a subset of remembered type '{self.value_node_pairs[0][0]}'. No update performed.")
                    new_list_types = set()
                    for new_type in new_inference_value:
                        new_list_types.add(f"list<{new_type}>")
                    v_table.bind(self.value_node_pairs[0][1].name, new_list_types)
                    vvvprint(f"ListLookup: inference: Updated variable '{self.value_node_pairs[0][1].name}' in variable table to new inferred type '{new_list_types}' based on new inference value '{new_inference_value}'.")
                    self.value_node_pairs[0] = (new_list_types, self.value_node_pairs[0][1])
                    vvvprint(f"ListLookup: inference: Updated value-node pair for list lookup to new inferred type '{new_list_types}'.")
                    return
            raise Exception(f"ListLookup: inference: {self.value_node_pairs[0][0]} is not compatible with old inference values '{old_inference_value}' and new inference value '{new_inference_value}'.", self)
            return
        vvvprint(f"ListLookup: inference: Old inference value matches remembered type. Updating variable '{self.value_node_pairs[0][1].name}' in variable table to new inference value '{new_inference_value}'...")
        new_list_types = set()
        for new_type in new_inference_value:
            new_list_types.add(f"list<{new_type}>")
        v_table.bind(self.value_node_pairs[0][1].name, new_list_types)
        vvvprint(f"ListLookup: inference: Updated variable '{self.value_node_pairs[0][1].name}' in variable table to new inferred type '{new_list_types}' based on new inference value '{new_inference_value}'.")
        self.value_node_pairs[0] = (new_list_types, self.value_node_pairs[0][1])
        vvvprint(f"ListLookup: inference: Updated value-node pair for list lookup to new inferred type '{new_list_types}'.")

                    
                        

            
        

@dataclass
class Unit(ASTNode):
    target: ASTNode
    unit_type: str

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        if target_type not in ["number", "decimal"]:
            if target_type == "UNKNOWN":
            raise BoshTypeError(f"Cannot apply unit '{self.unit_type}' to type '{target_type}'. Expected number or decimal.", self)
        return "time"

    def execute(self, env: Environment) -> Any:
        target_value = self.target.execute(env)
        match self.unit_type:
            case "seconds":
                return target_value * 1000  # Convert seconds to milliseconds
            case "minutes":
                return target_value * 60 * 1000  # Convert minutes to milliseconds
            case "hours":
                return target_value * 60 * 60 * 1000  # Convert hours to milliseconds
            case "days":
                return target_value * 24 * 60 * 60 * 1000  # Convert days to milliseconds
            case "weeks":
                return target_value * 7 * 24 * 60 * 60 * 1000  # Convert weeks to milliseconds
            case "months":
                return target_value * 30 * 24 * 60 * 60 * 1000  # Approximate conversion of months to milliseconds
            case "years":
                return target_value * 365 * 24 * 60 * 60 * 1000  # Approximate conversion of years to milliseconds
            case _:
                raise BoshRuntimeError(f"Unsupported unit type '{self.unit_type}'", self)

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        left_type = self.left.check(v_table, f_table) if isinstance(self.left, ASTNode) else self.left
        right_type = self.right.check(v_table, f_table) if isinstance(self.right, ASTNode) else self.right
        op = self.operator

        if left_type == "any" or right_type == "any":
            if op in ["eq", "neq", "lt", "gt", "gte", "lte", "or", "and"]:
                return "boolean"
            if op in ["plus", "minus", "div", "mult", "mod"]:
                return "any"
            # fallback: preserve previous behavior for unknown operators
            return "any" 
        
        if op in ["plus", "minus", "div", "mult", "mod"]:
            if left_type in ["number", "decimal"] and right_type in ["number", "decimal"]:
                return "decimal" if "decimal" in [left_type, right_type] else "number"
            elif op == "plus" and left_type == "text" and right_type == "text":
                return "text"
            else:
                raise BoshTypeError(f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'", self)
            
        elif op in ["eq", "neq"]:
            numeric_eq = (left_type in ["number", "decimal"] and right_type in ["number", "decimal"])
            null_eq = (left_type == "null" or right_type == "null")
            if left_type != right_type and not numeric_eq and not null_eq:
                raise BoshTypeError(f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'", self)
            return "boolean"
        
        elif op in ["or", "and"]:
            if left_type != "boolean" or right_type != "boolean":
                raise BoshTypeError(f"Logical operator '{op}' requires boolean operands, got '{left_type}' and '{right_type}'", self)
            return "boolean"
        
        elif op in ["lt", "gt", "gte", "lte"]:
            if left_type not in ["number", "decimal", "date", "time"] or right_type not in ["number", "decimal", "date", "time"]:
                raise BoshTypeError(f"Relational operator '{op}' requires numeric or temporal operands, got '{left_type}' and '{right_type}'.", self)
            return "boolean"
        
        else:
            raise BoshTypeError(f"Unsupported operator '{op}'", self)

    def execute(self, env: Environment) -> Any:
        match self.operator:
            case "plus":
                return self.left.execute(env) + self.right.execute(env)
            case "minus":
                return self.left.execute(env) - self.right.execute(env)
            case "mult":
                return self.left.execute(env) * self.right.execute(env)
            case "div":
                return self.left.execute(env) / self.right.execute(env)
            case "mod":
                return self.left.execute(env) % self.right.execute(env)
            case "eq":
                return self.left.execute(env) == self.right.execute(env)
            case "neq":
                return self.left.execute(env) != self.right.execute(env)
            case "or":
                return self.left.execute(env) or self.right.execute(env)
            case "and":
                return self.left.execute(env) and self.right.execute(env)
            case "lt":
                return self.left.execute(env) < self.right.execute(env)
            case "gt":
                return self.left.execute(env) > self.right.execute(env)
            case "lte":
                return self.left.execute(env) <= self.right.execute(env)
            case "gte":
                return self.left.execute(env) >= self.right.execute(env)
            case _:
                raise BoshRuntimeError(f"Unsupported operator '{self.operator}'", self)

@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        operand_type = self.operand.check(v_table, f_table)
        op = self.operator
        if op in ["-", "neg", "negative"]:
            if operand_type not in ["number", "decimal"]:
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.", self)
            return operand_type
        
        elif op in ["not_", "not", "!"]:
            if operand_type != "boolean":
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'boolean'.", self)
            return "boolean"
        
        elif op in ["floor", "ceiling", "round"]:
            if operand_type not in ["number", "decimal"]:
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.", self)
            return "number"
        
        elif op == "exponent":
            if operand_type not in ["number", "decimal"]:
                raise BoshTypeError(f"Unary operator 'exponent' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.", self)
            return "decimal"
        
        elif op == "length":
            is_list = isinstance(operand_type, str) and operand_type.startswith("list<") and operand_type.endswith(">")
            if operand_type != "text" and not is_list:
                raise BoshTypeError(f"Unary operator 'length' not supported for type '{operand_type}'. Expected 'text' or 'list'.", self)
            return "number"
    
        elif op in ["first", "last"]:
            is_list = isinstance(operand_type, str) and operand_type.startswith("list<") and operand_type.endswith(">")
            if operand_type != "text" and not is_list:
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'text' or 'list'.", self)
            if operand_type == "text":
                return "text"
            else:
                return operand_type[5:-1]
            
        else:
            raise BoshTypeError(f"Unsupported unary operator '{op}'", self)

    def execute(self, env):
        import math
        match self.operator:
            case "-":
                return -self.operand.execute(env)
            case "not":
                return not self.operand.execute(env)
            case "first":
                return self.operand.execute(env)[0]
            case "last":
                return self.operand.execute(env)[-1]
            case "floor":
                return math.floor(self.operand.execute(env))
            case "ceiling":
                return math.ceil(self.operand.execute(env))
            case "exponent":
                return math.exp(self.operand.execute(env))
            case "round":
                return int(round(self.operand.execute(env)))
            case _:
                raise BoshRuntimeError(f"Unsupported unary operator '{self.operator}'", self)

@dataclass
class AccessOp(ASTNode):
    target: Optional[ASTNode]
    operation: str
    argument: Optional[ASTNode] = None
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table) if self.target else None
        op = self.operation

        if op == "file_name":
            if target_type != "text":
                raise BoshTypeError(f"Cannot get file name of type '{target_type}'. Expected 'file' or 'folder'.", self)
            return "text"
        
        elif op == "age":
            if target_type != "text":
                raise BoshTypeError(f"Cannot get age of type '{target_type}'. Expected 'file' or 'folder'.", self)
            return "number"
        
        elif op in ["starts_with", "ends_with", "regex"]:
            if target_type != "text":
                raise BoshTypeError(f"Cannot apply operation '{op}' to type '{target_type}'. Expected 'text'.", self)

            if self.argument is not None:
                arg_type = self.argument.check(v_table, f_table)
                if arg_type != "text":
                    raise BoshTypeError(f"Argument for operation '{op}' must be of type 'text', got '{arg_type}'.", self)
            return "boolean"
        
        elif op == "unit":
            if target_type in ["number", "decimal"]:
                return "time"
            elif target_type == "time":
                return "number"
            else:
                raise BoshTypeError(f"Time units require a numeric, date, or time target, got '{target_type}'.", self)
        
        elif op == "now":
            return "date"
        
        elif op == "here":
            return "text"
        
        else:
            raise BoshTypeError(f"Unsupported access operation '{op}'", self)