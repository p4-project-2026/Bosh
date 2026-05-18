import os
from unittest import case
from .ast_base import *
import math
import datetime
import re

@dataclass
class NumberLiteral(ASTNode):
    value: int
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        self.child_return_types["self"] = ({"number"}, self) # remember the return type for inference
        return {"number"}
    
    def execute(self, env: Environment) -> float:
        return self.value
    
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # Number literals are only compatible with "number", "decimal", and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("NumberLiteral: inference: Number literals only return a single type, it should not be called during type inference. " \
        "something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
        "DONE"


@dataclass
class DecimalLiteral(ASTNode):
    value: float
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        self.child_return_types["self"] = ({"decimal"}, self) # remember the return type for inference
        return {"decimal"}
    
    def execute(self, env: Environment) -> float:
        return self.value

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # Decimal literals are only compatible with "decimal" and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("DecimalLiteral: inference: Decimal literals only return a single type, it should not be called during type inference. " \
        "something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
        "DONE"
@dataclass
class StringLiteral(ASTNode):
    value: str
    def  __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        self.child_return_types["self"] = ({"text"}, self) # remember the return type for inference
        return {"text"}

    def execute(self, env: Environment) -> str:
        return self.value

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # String literals are only compatible with "text" and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("StringLiteral: inference: String literals only return a single type, it should not be called during type inference. " \
        "something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
        "DONE"

@dataclass
class InterpolatedString(ASTNode):
    parts: List[ASTNode]
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        try:
            for part in self.parts:
                if part.check(v_table, f_table, inference_context) is None:
                    raise TraceError(node = self, cause = "Undefined variable in interpolated string")
            self.child_return_types["self"] = ({"text"}, self) # remember the return type for inference
            return {"text"}
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> str:
        result = ""
        for part in self.parts:
            value = part.execute(env)
            result += str(value)
        return result
    
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # Interpolated strings are only compatible with "text" and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("InterpolatedString: inference: Interpolated strings only return a single type, it should not be called during type inference. " \
        "something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
        "DONE"
        
@dataclass
class DateLiteral(ASTNode):
    value: str
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        return "date"
    
    def execute(self, env: Environment) -> datetime.datetime:
        try:
            return datetime.datetime.fromisoformat(self.value)
        except Exception as e:
            raise TraceError(node = self, cause = e)

@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        self.child_return_types["self"] = ({"boolean"}, self) # remember the return type for inference
        return {"boolean"}

    def execute(self, env: Environment) -> bool:
        return self.value

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # Boolean literals are only compatible with "boolean" and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("BooleanLiteral: inference: Boolean literals only return a single type, it should not be called during type inference. " \
        "something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
        "DONE"

@dataclass
class NullLiteral(ASTNode):
    def  __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        self.child_return_types["self"] = ({"null"}, self) # remember the return type for inference
        return {"null"}
    
    def execute(self, env: Environment) -> None:
        return None

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # Null literals are compatible with all types, so they can be narrowed to any type without error.
        raise Exception("NullLiteral: inference: Null literals only return a single type, it should not be called during type inference. " \
        "something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
        "DONE"

@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        try:
            self.child_return_types.clear()
            if len(self.elements) == 0:
                list_type = {EMPTY_LIST_TYPE}
                self.child_return_types["self"] = (list_type, self) # remember the return type for inference
                return list_type
            element_type = self.elements[0].check(v_table, f_table, inference_context)
            
            for elem in self.elements[1:]:
                elem_type = elem.check(v_table, f_table, inference_context)
                if elem_type != element_type:
                    raise Exception(f"List elements must all be of the same type, expected {element_type}, got {elem_type}", self)
                list_type = t_h.make_set_list_types(elem_type)
            self.child_return_types["element"] = (element_type.copy(), self.elements[0])# all elements have the same type, so we can just use the first one to remember the type for inference. this node will not be infered itself, it's just for consistency and potential future use.
            self.child_return_types["self"] = (list_type.copy(), self) # remember the return type for inference
            
            return list_type
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> List[Any]:
        try:
            return [elem.execute(env) for elem in self.elements]
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        # List literals are only compatible with "list<elem_type>" and "any" types, so if the new inference value is not compatible, raise an error.
        raise Exception("ListLiteral: inference: List literals only returns a single type, it should not be be called during type inference. " \
        "something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)

@dataclass
class Identifier(ASTNode):
    name: str
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        try:
            self.child_return_types.clear()
            vvvprint(f"Identifier: check: Looking up variable '{self.name}' in variable table...")
            var_type = v_table.lookup(self.name)
            vvvprint(f"Identifier: check: Variable '{self.name}' found with type '{var_type}'")
            self.child_return_types["self"] = (var_type.copy(), self)
            vvvprint(f"Identifier: check: Remembered type for variable '{self.name}' returned set to '{var_type}' for inference.")
            return var_type
        except Exception as e:
            raise TraceError(node = self, cause=e)


    def execute(self, env: Environment) -> Any:
        vvvprint(f"Identifier: execute: Looking up variable '{self.name}'...")
        try:
            vvvprint(f"Identifier: execute: Variable '{self.name}' found. Retrieving value...")
            value = env.lookup_variable(self.name)
            vvvprint(f"Identifier: execute: Value of variable '{self.name}': {value}")
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e)


    def inference(
        self,
        v_table: ScopeStack,
        f_table: FuncTable,
        inference_context: InferenceContext,
        old_inference_value: set[str],
        new_inference_value: set[str],
    ) -> None:
        try:
            vvvprint(f"Identifier: inference: Starting inference for variable '{self.name}' with old inference value '{old_inference_value}' and new inference value '{new_inference_value}'...")
            if "self" not in self.child_return_types:
                raise Exception(f"Identifier: inference: No type information available for variable '{self.name}' during type inference. {self} has not been checked.", self)
            vvvprint(f"Identifier: inference: Current child return types for variable '{self.name}': {self.child_return_types}")

            vvvprint(f"Identifier: inference: Checking if old inference value '{old_inference_value}' matches remembered type for variable '{self.name}'...")
            remembered_type = self.child_return_types["self"][0].copy()
            vvvprint(f"Identifier: inference: Remembered return type for variable '{self.name}': {remembered_type}")

            vvvprint(f"Identifier: inference: Comparing old inference value '{old_inference_value}' with remembered type '{remembered_type}' for variable '{self.name}'...")
            if remembered_type != old_inference_value:
                raise Exception(f"Identifier: inference: Old inference value '{old_inference_value}' does not match remembered type '{remembered_type}' for variable '{self.name}'. something went wrong in type inference pathing.", self)
            vvvprint(f"Identifier: inference: Old inference value '{old_inference_value}' matches remembered type for variable '{self.name}'.")


            vvvprint(f"Identifier: inference: retrieving current type for variable '{self.name}' from variable table for inference...")
            current_type = v_table.lookup(self.name).copy()
            vvvprint(f"Identifier: inference: Current type for variable '{self.name}' from variable table: {current_type}")

            vvvprint(f"Identifier: inference: Checking compatibility of new inference value '{new_inference_value}' with current type '{current_type}' for variable '{self.name}'...")
            if not t_h.is_compatible(current_type, new_inference_value):
                raise Exception(f"Identifier: inference: New inference value '{new_inference_value}' is incompatible with current type '{current_type}' for variable '{self.name}'. something went wrong in type inference.", self)
            vvvprint(f"Identifier: inference: New inference value '{new_inference_value}' is compatible with current type '{current_type}' for variable '{self.name}'.")

            vvvprint(f"Identifier: inference: Checking if new inference value '{new_inference_value}' narrows the current type '{current_type}' for variable '{self.name}'...")
            narrowed = t_h.narrow(current_type, new_inference_value)
            if narrowed == current_type:
                raise Exception(
                                f"Identifier: inference path reached this node, but no narrowing occurred. "
                                f"current={current_type}, new={new_inference_value}. "
                                f"This probably means the parent passed a non-narrowing inference request.",
                                self
                                )

            vvvprint(f"Identifier: inference: New inference value '{new_inference_value}' narrows the current type for variable '{self.name}'. Updating variable table and remembered type...")
            v_table.bind(self.name, narrowed.copy())
            self.child_return_types["self"] = (narrowed.copy(), self)
            inference_context.mark_infered()
            vvvprint(f"Identifier: inference: Updated variable '{self.name}' in variable table to new inferred type '{narrowed}'. Remembered type for variable '{self.name}' updated to '{narrowed}' for inference. Inference marked as updated in inference context.")
            return
            "DONE"
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class TaskCall(ASTNode):
    name: str
    arguments: Optional[List[ASTNode]] = None
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
        try:
            self.child_return_types.clear()

            signature = f_table.lookup(self.name)
            arguments = self.arguments or []

            

                
            if len(arguments) != len(signature.param_types):
                raise Exception(f"Task '{self.name}' expects {len(signature.param_types)} arguments, but got {len(arguments)}", self)
        
            for i, arg in enumerate(arguments):
                    
                arg_type = arg.check(
                    v_table=v_table, 
                    f_table=f_table,
                    inference_context=inference_context
                    )
                    
                argument_name = signature.param[i]
                expected_type = signature.param_types[argument_name].copy()
                
                if not t_h.is_compatible(arg_type, expected_type):
                    raise Exception(f"Argument {argument_name} of task '{self.name}' expects type '{expected_type}', but got '{arg_type}'", self)
                
                narrowed_arg_type = t_h.narrow(arg_type, expected_type)
                if arg_type != narrowed_arg_type:
                    
                    arg.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=arg_type.copy(),
                        new_inference_value=narrowed_arg_type.copy()
                        )
                            
                    arg_type = narrowed_arg_type

                self.child_return_types[f"arg_{i}"] = (arg_type.copy(), arg)
                vvvprint(f"Task Call: check: Argument {i+1} for task '{self.name}' checked with type '{arg_type}'. Remembered type for argument '{argument_name}' set to '{arg_type}' for inference.")

                    
            if signature.return_type is not None:
                self.child_return_types["self"] = (signature.return_type.copy(), self)
                return signature.return_type.copy()
            
            return None
        except Exception as e:
            raise TraceError(node = self, cause=e)

    def execute(self, env: Environment) -> Any:
        try:
            vvvprint(f"Task Call: Looking up task '{self.name}'...")
            task_func = env.get_function(self.name)
            vvvprint(f"Task Call: Task '{self.name}' found: {task_func}")

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
            
            vvvprint(f"Task Call: Executing body of task '{self.name}'...")
            result = task_func.body.execute(env)
            vvvprint(f"Task Call: Body of task '{self.name}' executed successfully. Result: {result}")
            return result
        except TraceError as e:
            raise TraceError(node = self,cause = e)

    def inference(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, old_inference_value: set[str], new_inference_value: set[str]) -> None:
        vvvprint(f"Task Call: does not implement inference, but can end up on the inference path.")

@dataclass
class ListLookup(ASTNode):
    target: ASTNode
    index: ASTNode
    def  __post_init__(self):
        super().__init__()
    
        
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        try:
            self.child_return_types.clear()

            index_type = self.index.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            if index_type is None:
                raise Exception("ListLookup: List index cannot be of type 'None'", self)
            
            valid_index_types = {"number"}
            if not t_h.is_compatible(index_type, valid_index_types):
                raise Exception(f"ListLookup: List index must be of type 'number', got '{index_type}'", self)
            
            if index_type != {"number"}:
                self.index.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=index_type.copy(),
                    new_inference_value={"number"}
                    )
                
                index_type = {"number"}
            
            self.child_return_types["index"] = (index_type.copy(), self.index)

            target_types = self.target.check(
                v_table=v_table,
                f_table=f_table,
                inference_context=inference_context
                )
                        
            # check if any of the target types are can be a list type and if so, extract the element types.
            
            if not target_types:
                raise Exception(f"ListLookup: Type Check Failed: Target of list lookup cannot be of type 'None'", self)
            
            if not t_h.has_list_type(target_types):
                raise Exception(f"ListLookup: Type Check Failed: Target of list lookup must be a list type, got '{target_types}'", self)
            
            valid_target_types = t_h.get_all_list_types(target_types)

            if valid_target_types != target_types:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=target_types.copy(),
                    new_inference_value=valid_target_types.copy()
                    )
                
                target_types = valid_target_types
                vvvprint(f"ListLookup: check: Target types narrowed to '{target_types}' for list lookup.")

            self.child_return_types["target"] = (target_types.copy(), self.target)

            
            return_types = t_h.get_list_element_types(target_types)
            
            self.child_return_types["self"] = (return_types.copy(), self)
            return return_types
        except Exception as e:
            raise TraceError(node = self, cause = e)
    
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
            index_value = self.index.execute(env)
            return target_value[int(index_value)]
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]
                ) -> None:
        try:
            
            if "self" not in self.child_return_types:
                raise Exception(f"ListLookup: inference: No type information available for list lookup during type inference {self} has not been checked.", self)
            
            remembered_types = self.child_return_types["self"][0].copy()

            if remembered_types != old_inference_value:
                raise Exception(f"ListLookup: inference: Old inference value '{old_inference_value}' does not match remembered type '{remembered_types}' for list lookup. something went wrong in type inference pathing.", self)
            if not t_h.is_compatible(remembered_types, new_inference_value):
                raise Exception(f"ListLookup: inference: New inference value '{new_inference_value}' is incompatible with remembered type '{remembered_types}' for list lookup. something went wrong.", self)

            narrowed = t_h.narrow(remembered_types, new_inference_value)

            if narrowed == remembered_types:
                raise Exception(
                                f"ListLookup: inference path reached this node, but no narrowing occurred. "
                                f"remembered={remembered_types}, new={new_inference_value}. "
                                f"This probably means the parent passed a non-narrowing inference request.", 
                                self
                                )
            

            self.child_return_types["self"] = (narrowed.copy(), self)

            list_types = t_h.make_set_list_types(narrowed)
            target_old_types = self.child_return_types["target"][0].copy()
            self.target.inference(
                v_table=v_table,
                f_table=f_table,
                inference_context=inference_context,
                old_inference_value=target_old_types,
                new_inference_value=list_types.copy()
                )
            
            self.child_return_types["target"] = (list_types.copy(), self.target)

        except Exception as e:
            raise TraceError(node = self, cause = e)    

@dataclass
class Unit(ASTNode):
    target: ASTNode
    unit_type: str
    def __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable,  inference_context: InferenceContext) -> set[str]:
        try:
            self.child_return_types.clear()
            target_type = self.target.check(v_table=v_table,
                                             f_table=f_table,
                                             inference_context=inference_context
                                             )
            
            possible_types = {"number", "decimal"}
            if not t_h.is_compatible(target_type, possible_types):
                raise BoshTypeError(f"Cannot apply unit '{self.unit_type}' to type '{target_type}'. Expected number or decimal.", self)
            
            narrowed = t_h.narrow(target_type, possible_types)
            
            if narrowed != target_type:
                self.target.inference(v_table=v_table,
                                      f_table=f_table,
                                      inference_context=inference_context,
                                      old_inference_value=target_type.copy(),
                                      new_inference_value=narrowed.copy()
                                      )
                
                target_type = narrowed.copy()

            self.child_return_types["target"] = (target_type.copy(), self.target)
            self.child_return_types["self"] = ({"time"}, self) # the return type of a unit is always time, so we can just set it directly without needing to remember it for inference.
            return {"time"}
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> Any:
        try:
            target_value = self.target.execute(env)
            match self.unit_type:
                case "second":
                    return target_value * 1000  # Convert seconds to milliseconds
                case "minute":
                    return target_value * 60 * 1000  # Convert minutes to milliseconds
                case "hour":
                    return target_value * 60 * 60 * 1000  # Convert hours to milliseconds
                case "day":
                    return target_value * 24 * 60 * 60 * 1000  # Convert days to milliseconds
                case "week":
                    return target_value * 7 * 24 * 60 * 60 * 1000  # Convert weeks to milliseconds
                case "month":
                    return target_value * 30 * 24 * 60 * 60 * 1000  # Approximate conversion of months to milliseconds
                case "year":
                    return target_value * 365 * 24 * 60 * 60 * 1000  # Approximate conversion of years to milliseconds
                case _:
                    raise TraceError(node = self, cause = f"Unsupported unit type '{self.unit_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]
                ) -> None:
            raise Exception(
                            f"Unit inference is not supported because the return type of a unit is always 'time'. "
                            f"If you are seeing this error, something went wrong in inference pathing. "
                            f"new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}",
                            self
                            )


@dataclass  
class TypeCast(ASTNode):
    target: ASTNode
    target_type: str

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
            original_type = self.target.check(v_table, f_table)
            if self.target_type not in ["number", "decimal", "text", "boolean", "date"]:
                raise TraceError(node = self, cause = f"Unsupported target type for type cast: '{self.target_type}'")
            if original_type == self.target_type:
                return original_type
            # Weak casting: number -> float -> string, boolean -> string, date -> string
            if self.target_type == "text":
                if original_type in ["number", "decimal", "boolean", "date"]:
                    return "text"
            if self.target_type in ["number", "decimal"]:
                if original_type in ["number", "decimal"]:
                    return self.target_type

            # Strong casting: float -> number, string -> number/decimal/boolean/date (if possible)
            if original_type == "text":
                if self.target_type in ["number", "decimal", "boolean", "date"]:
                    return self.target_type
            
            raise TraceError(node = self, cause = f"Cannot cast from '{original_type}' to '{self.target_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> Any:
        try:
            value = self.target.execute(env)
            match self.target_type:
                case "number":
                    return int(value)
                case "decimal":
                    return float(value)
                case "text":
                    if isinstance(value, bool):
                        return "true" if value else "false"
                    return str(value)
                case "boolean":
                    return bool(value)
                case "date":
                    if isinstance(value, (datetime.datetime, str)):
                        return datetime.datetime.fromisoformat(str(value))
                    raise TraceError(node = self, cause = f"Cannot cast value of type '{type(value).__name__}' to 'date'")
                case _:
                    raise TraceError(node = self, cause = f"Unsupported target type for type cast: '{self.target_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass  
class TypeCast(ASTNode):
    target: ASTNode
    target_type: str

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
            original_type = self.target.check(v_table, f_table)
            if self.target_type not in ["number", "decimal", "text", "boolean", "date"]:
                raise TraceError(node = self, cause = f"Unsupported target type for type cast: '{self.target_type}'")
            if original_type == self.target_type:
                return original_type
            # Weak casting: number -> float -> string, boolean -> string, date -> string
            if self.target_type == "text":
                if original_type in ["number", "decimal", "boolean", "date"]:
                    return "text"
            if self.target_type in ["number", "decimal"]:
                if original_type in ["number", "decimal"]:
                    return self.target_type

            # Strong casting: float -> number, string -> number/decimal/boolean/date (if possible)
            if original_type == "text":
                if self.target_type in ["number", "decimal", "boolean", "date"]:
                    return self.target_type
            
            raise TraceError(node = self, cause = f"Cannot cast from '{original_type}' to '{self.target_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> Any:
        try:
            value = self.target.execute(env)
            match self.target_type:
                case "number":
                    return int(value)
                case "decimal":
                    return float(value)
                case "text":
                    if isinstance(value, bool):
                        return "true" if value else "false"
                    return str(value)
                case "boolean":
                    return bool(value)
                case "date":
                    if isinstance(value, (datetime.datetime, str)):
                        return datetime.datetime.fromisoformat(str(value))
                    raise TraceError(node = self, cause = f"Cannot cast value of type '{type(value).__name__}' to 'date'")
                case _:
                    raise TraceError(node = self, cause = f"Unsupported target type for type cast: '{self.target_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        try:
            self.child_return_types.clear()
            left_type = self.left.check(v_table=v_table,
                                        f_table=f_table,
                                        inference_context=inference_context
                                        )
            right_type = self.right.check(v_table=v_table, 
                                          f_table=f_table, 
                                          inference_context=inference_context
                                          )
            
            if left_type is None or right_type is None:
                raise Exception(
                                f"Binary operator check failed: left or right operand has no type. "
                                f"left_type: {left_type}, right_type: {right_type}",
                                self
                                )
            
            op = self.operator

            match op:
                    
                case  "plus" | "minus" | "mult" | "div":
                    valid_input_types = {"number", "decimal"}
                    if not t_h.is_compatible(left_type, valid_input_types):
                        raise Exception(
                                        f"Binary operator '{op}' not supported for left type '{left_type}'. "
                                        f"Expected number or decimal.",
                                        self
                                        )

                    if not t_h.is_compatible(right_type, valid_input_types):
                        raise Exception(
                                        f"Binary operator '{op}' not supported for right type '{right_type}'. "
                                        f"Expected number or decimal.",
                                        self
                                        )

                    left_narrowed = t_h.narrow(left_type, valid_input_types)
                    right_narrowed = t_h.narrow(right_type, valid_input_types)

                    if left_narrowed != left_type:
                        self.left.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=left_type.copy(),
                        new_inference_value=left_narrowed.copy(),
                        )

                    if right_narrowed != right_type:
                        self.right.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=right_type.copy(),
                        new_inference_value=right_narrowed.copy(),
                        )

                    self.child_return_types["left"] = (left_narrowed.copy(), self.left)
                    self.child_return_types["right"] = (right_narrowed.copy(), self.right)
                    return_types = set()

                    if "number" in left_narrowed and "number" in right_narrowed:
                        return_types.add("number")
                    if "decimal" in left_narrowed or "decimal" in right_narrowed:
                        return_types.add("decimal")
                    
                    if not return_types:
                        #Sanity check.
                        raise Exception(
                        f"Internal type error: numeric operator '{op}' produced no return type "
                        f"from left={left_narrowed}, right={right_narrowed}",
                        self
                        )

                    self.child_return_types["self"] = (return_types.copy(), self)
                    return return_types
                    
                case  "mod":
                    valid_input_types = {"number"}
                    if not t_h.is_compatible(left_type, valid_input_types):
                        raise Exception(
                                        f"Binary operator 'mod' only supports 'number' types. Got left type '{left_type}'.",
                                        self
                                        )

                    if not t_h.is_compatible(right_type, valid_input_types):
                        raise Exception(
                                        f"Binary operator 'mod' only supports 'number' types. Got right type '{right_type}'.",
                                        self
                                        )

                    if left_type != {"number"}:
                        self.left.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=left_type.copy(),
                        new_inference_value={"number"},
                        )

                    if right_type != {"number"}:
                        self.right.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=right_type.copy(),
                        new_inference_value={"number"},
                        )

                    self.child_return_types["left"] = ({"number"}, self.left)
                    self.child_return_types["right"] = ({"number"}, self.right)
                    self.child_return_types["self"] = ({"number"}, self)
                    return {"number"}

                case "eq" | "neq" | "lt" | "gt" | "lte" | "gte":
                    if left_type == right_type:
                        self.child_return_types["left"] = (left_type.copy(), self.left)
                        self.child_return_types["right"] = (right_type.copy(), self.right)
                        self.child_return_types["self"] = ({"boolean"}, self)
                        return {"boolean"}
                    if not t_h.is_compatible(left_type, right_type):
                        raise Exception(
                                        f"Binary operator '{op}' only supports operands of compatible types. "
                                        f"Got left type '{left_type}' and right type '{right_type}'.",
                                        self
                                        )
                    
                    narrowed = t_h.narrow(left_type, right_type)
                    if narrowed != left_type:
                        self.left.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=left_type.copy(),
                        new_inference_value=narrowed.copy(),
                        )

                    self.child_return_types["left"] = (narrowed.copy(), self.left)
                    if narrowed != right_type:
                        self.right.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=right_type.copy(),
                        new_inference_value=narrowed.copy(),
                        )

                    self.child_return_types["right"] = (narrowed.copy(), self.right)
                    self.child_return_types["self"] = ({"boolean"}, self)
                    return {"boolean"}

                case "or" | "and":
                    valid_input_types = {"boolean"}
                    if not t_h.is_compatible(left_type, valid_input_types):
                        raise Exception(
                                        f"Binary operator '{op}' not supported for left type '{left_type}'. "
                                        f"Expected boolean.",
                                        self
                                        )
                    
                    if not t_h.is_compatible(right_type, valid_input_types):
                        raise Exception(
                                        f"Binary operator '{op}' not supported for right type '{right_type}'. "
                                        f"Expected boolean.",
                                        self
                                        )
                    
                    if left_type != {"boolean"}:
                        self.left.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=left_type.copy(),
                        new_inference_value={"boolean"},
                        )

                    if right_type != {"boolean"}:
                        self.right.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=right_type.copy(),
                        new_inference_value={"boolean"},
                        )

                    self.child_return_types["left"] = ({"boolean"}, self.left)
                    self.child_return_types["right"] = ({"boolean"}, self.right)
                    self.child_return_types["self"] = ({"boolean"}, self)
                    return {"boolean"}
               
                case _:
                    raise Exception(f"Binary operator '{op}' is not supported", self)

        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> Any:
        try:
            left_val = self.left.execute(env) if isinstance(self.left, ASTNode) else self.left
            right_val = self.right.execute(env) if isinstance(self.right, ASTNode) else self.right
            match self.operator:
                case "plus":
                    # datetime + milliseconds
                    if isinstance(left_val, datetime.datetime) and isinstance(right_val, (int, float)):
                        return left_val + datetime.timedelta(milliseconds=right_val)
                    # milliseconds + datetime -> swap
                    if isinstance(right_val, datetime.datetime) and isinstance(left_val, (int, float)):
                        return right_val + datetime.timedelta(milliseconds=left_val)
                    # string concatenation
                    if isinstance(left_val, str) or isinstance(right_val, str):
                        if isinstance(left_val, bool):
                            left_val = "true" if left_val else "false"
                        return str(left_val) + str(right_val)
                    # fallback to python add (may raise)
                    return left_val + right_val
                case "minus":
                    # datetime - datetime -> timedelta
                    if isinstance(left_val, datetime.datetime) and isinstance(right_val, datetime.datetime):
                        return left_val - right_val
                    # datetime - milliseconds
                    if isinstance(left_val, datetime.datetime) and isinstance(right_val, (int, float)):
                        return left_val - datetime.timedelta(milliseconds=right_val)
                    # numeric subtraction
                    if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                        return left_val - right_val
                    return left_val - right_val
                case "mult":
                    return left_val * right_val
                case "div":
                    return left_val / right_val
                case "mod":
                    return left_val % right_val
                case "pow":
                    return left_val ** right_val
                case "eq":
                    if type(left_val) != type(right_val):
                        if (type(left_val) in [int, float] and type(right_val) in [int, float]):
                            pass
                        else:
                            return False
                    return left_val == right_val
                case "neq":
                    if type(left_val) != type(right_val):
                        if (type(left_val) in [int, float] and type(right_val) in [int, float]):
                            pass
                        else:
                            return True
                    return left_val != right_val
                case "eq_type" | "neq_type":
                    if right_val in ["folder", "file"]:
                        if isinstance(left_val, str):
                            if right_val == "folder":
                                return os.path.isdir(left_val)
                            else:
                                return os.path.isfile(left_val)
                        else:
                            raise TraceError(node = self, cause = f"Left operand must be a string when comparing to 'file' or 'folder', got '{type(left_val).__name__}'")
                    if self.operator == "eq_type":
                        return python_type_to_bosh_type(type(left_val)) == right_val
                    return python_type_to_bosh_type(type(left_val)) != right_val
                case "or":
                    return bool(left_val) or bool(right_val)
                case "and":
                    return bool(left_val) and bool(right_val)
                case "lt":
                    return left_val < right_val
                case "gt":
                    return self.left.execute(env) > self.right.execute(env)
                case "loet":
                    return self.left.execute(env) <= self.right.execute(env)
                case "goet":
                    return self.left.execute(env) >= self.right.execute(env)
                case _:
                    raise TraceError(node = self, cause = f"Unsupported operator '{self.operator}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]
                ) -> None:
        try:
            if "self" not in self.child_return_types:
                raise Exception(f"BinaryOp inference: No type information available for binary operator during inference. This node has not been checked. Node: {self}", self)
            if old_inference_value != self.child_return_types["self"][0]:
                raise Exception(f"BinaryOp inference: Old inference value '{old_inference_value}' does not match remembered return type '{self.child_return_types['self'][0]}' for binary operator. Something went wrong in the inference pathing. Node: {self}", self)
            if not t_h.is_compatible(new_inference_value, self.child_return_types["self"][0]):
                raise Exception(f"BinaryOp inference: New inference value '{new_inference_value}' is not compatible with remembered return type '{self.child_return_types['self'][0]}' for binary operator. Something went wrong in the inference pathing. Node: {self}", self)
            
            match self.operator:
                case  "plus" | "minus" | "mult" | "div":
                    if new_inference_value == {"number"}:
                        new_left_inference = {"number"}
                        new_right_inference = {"number"}
                        if self.child_return_types["left"][0] != new_left_inference:
                            self.left.inference(
                                v_table=v_table,
                                f_table=f_table,
                                inference_context=inference_context,
                                old_inference_value=self.child_return_types["left"][0].copy(),
                                new_inference_value=new_left_inference.copy(),
                            )
    
                            self.child_return_types["left"] = (new_left_inference.copy(), self.left)
    
                        if self.child_return_types["right"][0] != new_right_inference:
                            self.right.inference(
                                v_table=v_table,
                                f_table=f_table,
                                inference_context=inference_context,
                                old_inference_value=self.child_return_types["right"][0].copy(),
                                new_inference_value=new_right_inference.copy(),
                            )
    
                            self.child_return_types["right"] = (new_right_inference.copy(), self.right)
    
                        self.child_return_types["self"] = ({"number"}, self)
                        return
                    
                    else:
                        left_values = self.child_return_types["left"][0]
                        right_values = self.child_return_types["right"][0]
                        if not "decimal" in left_values:
                            # left cannot explain decimal result,
                            # so right must be decimal
                            new_right_values = {"decimal"}
                            self.right.inference(
                                v_table=v_table,
                                f_table=f_table,
                                inference_context=inference_context,
                                old_inference_value=right_values.copy(),
                                new_inference_value=new_right_values.copy(),
                            )
                            right_values = new_right_values.copy()
    
                        
                        elif not "decimal" in right_values:
                            # right cannot explain decimal result,
                            # so left must be decimal
                            new_left_values = {"decimal"}
                            self.left.inference(
                                v_table=v_table,
                                f_table=f_table,
                                inference_context=inference_context,
                                old_inference_value=left_values.copy(),
                                new_inference_value=new_left_values.copy(),
                            )
                            left_values = new_left_values.copy()
    
                        self.child_return_types["left"] = (left_values.copy(), self.left)
                        self.child_return_types["right"] = (right_values.copy(), self.right)
                        self.child_return_types["self"] = (new_inference_value, self)
            
                        return
                
                case "mod":
                    raise Exception(
                                    f"Inference for 'mod' is not supported because 'mod' always returns 'number'. "
                                    f"If you are seeing this, something went wrong in inference pathing. "
                                    f"new_inference_value: {new_inference_value}, "
                                    f"old_inference_value: {old_inference_value}",
                                    self
                                    )
                
                case "eq" | "neq" | "lt" | "gt" | "lte" | "gte":
                    raise Exception(
                                    f"Inference for comparison operator '{self.operator}' is not supported because "
                                    f"comparisons always return 'boolean'. If you are seeing this, something went "
                                    f"wrong in inference pathing. new_inference_value: {new_inference_value}, "
                                    f"old_inference_value: {old_inference_value}",
                                    self
                                    )
                
                case "or" | "and":
                    raise Exception(
                                    f"Inference for logical operator '{self.operator}' is not supported because "
                                    f"logical operators always return 'boolean'. If you are seeing this, something "
                                    f"went wrong in inference pathing. new_inference_value: {new_inference_value}, "
                                    f"old_inference_value: {old_inference_value}",
                                    self
                                    )
    
                case _:
                    raise Exception(f"Unsupported operator '{self.operator}' for inference in BinaryOp. Node: {self}", self)
        
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        try:
            self.child_return_types.clear()
            operand_type = self.operand.check(v_table=v_table,
                                              f_table=f_table,
                                              inference_context=inference_context
                                              )
            
            op = self.operator
            match op:
                case "-" | "neg" | "negative":
                    valid_input_types = {"number", "decimal"}
                    if not t_h.is_compatible(operand_type, valid_input_types):
                        raise Exception(
                                        f"Unary operator '{op}' not supported for type '{operand_type}'. "
                                        f"Expected number or decimal.",
                                        self
                                        )
                    
                    narrowed = t_h.narrow(operand_type, valid_input_types)
                    if narrowed != operand_type:
                        self.operand.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=operand_type.copy(),
                        new_inference_value=narrowed.copy(),
                        )

                    self.child_return_types["operand"] = (narrowed.copy(), self.operand)
                    self.child_return_types["self"] = (narrowed.copy(), self)
                    return narrowed
                
                case "not_" | "not" | "!":
                    valid_input_types = {"boolean"}
                    if not t_h.is_compatible(operand_type, valid_input_types):
                        raise Exception(
                                        f"Unary operator '{op}' not supported for type '{operand_type}'. "
                                        f"Expected boolean.",
                                        self
                                        )
                    
                    if operand_type != {"boolean"}:
                        self.operand.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=operand_type.copy(),
                        new_inference_value={"boolean"},
                        )

                    self.child_return_types["operand"] = ({"boolean"}, self.operand)
                    self.child_return_types["self"] = ({"boolean"}, self)
                    return {"boolean"}
                
                case "floor" | "ceiling" | "round":
                    valid_input_types = {"number", "decimal"}
                    if not t_h.is_compatible(operand_type, valid_input_types):
                        raise Exception(
                                        f"Unary operator '{op}' not supported for type '{operand_type}'. "
                                        f"Expected number or decimal.",
                                        self
                                        )
                    
                    narrowed = t_h.narrow(operand_type, valid_input_types)
                    if narrowed != operand_type:
                        self.operand.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=operand_type.copy(),
                        new_inference_value=narrowed.copy(),
                        )

                    self.child_return_types["operand"] = (narrowed.copy(), self.operand)
                    self.child_return_types["self"] = ({"number"}, self)
                    return {"number"}
                
                case "exponent":
                    valid_input_types = {"number", "decimal"}
                    if not t_h.is_compatible(operand_type, valid_input_types):
                        raise Exception(
                                        f"Unary operator 'exponent' not supported for type '{operand_type}'. "
                                        f"Expected number or decimal.",
                                        self
                                        )
                    
                    narrowed = t_h.narrow(operand_type, valid_input_types)
                    if narrowed != operand_type:
                        self.operand.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=operand_type.copy(),
                        new_inference_value=narrowed.copy(),
                        )

                    self.child_return_types["operand"] = (narrowed.copy(), self.operand)
                    self.child_return_types["self"] = (narrowed.copy(), self)
                    return narrowed
                
                case "length":    
                    if not t_h.has_list_type(operand_type):
                        raise Exception(
                                        f"Unary operator 'length' not supported for type '{operand_type}'. "
                                        f"Expected a list.",
                                        self
                                        )
                    
                    if t_h.has_non_list_type(operand_type):
                        new_operand_type = t_h.get_all_list_types(operand_type)
                        self.operand.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=operand_type.copy(),
                        new_inference_value=new_operand_type.copy(),
                        )

                        operand_type = new_operand_type.copy()

                    self.child_return_types["operand"] = (operand_type.copy(), self.operand)
                    self.child_return_types["self"] = ({"number"}, self)
                    return {"number"}
                
                case "first" | "last":
                    if not t_h.has_list_type(operand_type):
                        raise Exception(
                                        f"Unary operator '{op}' not supported for type '{operand_type}'. "
                                        f"Expected a list.",
                                        self
                                        )
                    
                    if t_h.has_non_list_type(operand_type):
                        new_operand_type = t_h.get_all_list_types(operand_type)
                        self.operand.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=operand_type.copy(),
                        new_inference_value=new_operand_type.copy(),
                        )

                        operand_type = new_operand_type.copy()

                    self.child_return_types["operand"] = (operand_type.copy(), self.operand)
                    return_type = t_h.get_list_element_types(operand_type)
                    self.child_return_types["self"] = (return_type.copy(), self)
                    return return_type
                
                case _:
                    raise Exception(f"Unsupported unary operator '{op}'", self)
        
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env):
        try:
            match self.operator:
                case "neg":
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
                case "round":
                    return int(round(self.operand.execute(env)))
                case "sqrt":
                    return math.sqrt(self.operand.execute(env))
                case _:
                    raise TraceError(node = self, cause = f"Unsupported unary operator '{self.operator}'")
                
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]
                ) -> None:
        
        if "self" not in self.child_return_types:
            raise Exception(f"UnaryOp inference: No type information available for unary operator during inference. This node has not been checked. Node: {self}", self)
        remembered_types = self.child_return_types["self"][0]
        if old_inference_value != remembered_types:
            raise Exception(f"UnaryOp inference: Old inference value '{old_inference_value}' does not match remembered return type '{remembered_types}' for unary operator. "
                            f"Something went wrong in the inference pathing. Node: {self}", self)
        if not t_h.is_compatible(new_inference_value, remembered_types):
            raise Exception(f"UnaryOp inference: New inference value '{new_inference_value}' is not compatible with remembered return type '{remembered_types}' for unary operator. "
                            f"Something went wrong in the inference pathing. Node: {self}", self)
        if old_inference_value == new_inference_value:
            raise Exception(f"UnaryOp inference: New inference value is the same as the old inference value '{old_inference_value}' for unary operator. "
                            f"This probably means the parent passed a non-narrowing inference request. Node: {self}", self)
        
        match self.operator:
            
            case "-" | "neg" | "negative" | "exponent":
                
                new_operand_inference = new_inference_value.copy()
                self.operand.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=self.child_return_types["operand"][0].copy(),
                        new_inference_value=new_operand_inference.copy(),
                        )
                    
                self.child_return_types["operand"] = (new_operand_inference.copy(), self.operand)
                self.child_return_types["self"] = (new_inference_value.copy(), self)
                return
            
            
            case "not_" | "not" | "!":
                raise Exception(f"Inference for 'not' operator is not supported because it only supports 'boolean' types and returns 'boolean', so there is no need for inference. "
                                f"If you are seeing this error, it means something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
            case "floor" | "ceiling" | "round":
                raise Exception(f"Inference for 'floor', 'ceiling', and 'round' operators is not supported because they only support 'number' and 'decimal' types and return 'number', so there is no need for inference. "
                                f"If you are seeing this error, it means something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
            case "length":
                raise Exception(f"Inference for 'length' operator is not supported because it only supports text and list types and returns 'number', so there is no need for inference. "
                                f"If you are seeing this error, it means something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
            
            case "first" | "last":
                self.child_return_types["self"] = (new_inference_value.copy(), self)
                new_list_inference = t_h.make_set_list_types(new_inference_value)
                self.operand.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=self.child_return_types["operand"][0].copy(),
                    new_inference_value=new_list_inference.copy(),
                    )
                
                self.child_return_types["operand"] = (new_list_inference.copy(), self.operand)
                return
            
            case _:
                raise Exception(f"Inference for unary operator '{self.operator}' is not supported. If you are seeing this error, it means something went wrong somewhere. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)

@dataclass
class AccessOp(ASTNode):
    target: Optional[ASTNode]
    operation: str
    argument: Optional[ASTNode] = None
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        try:
            self.child_return_types.clear()
            vvprint(f"AccessOp: Checking access operation '{self.operation}'...")

            target_type = self.target.check(v_table=v_table, f_table=f_table, inference_context=inference_context) if self.target else None
            op = self.operation



            match op:
                
                case "file_name":
                    if target_type is None:
                        raise Exception(f"Access operation '{op}' requires a target, but no target was provided.")
                    if not t_h.contains(target_type, "text"):
                        raise Exception(f"Cannot get file name from type '{target_type}'. {op} Expected 'text'.")
                    
                    if target_type != {"text"}:
                        self.target.inference(
                            v_table=v_table,
                            f_table=f_table,
                            inference_context=inference_context,
                            old_inference_value=target_type.copy(),
                            new_inference_value={"text"},
                        )
                        target_type = {"text"}
                    
                    self.child_return_types["target"] = (target_type.copy(), self.target)
                    self.child_return_types["self"] = ({"text"}, self)

                    vvprint(f"AccessOp: Operation 'file_name' on target type '{target_type}' is valid. Returning 'text'.")
                    return {"text"}
                
                case "age":
                    if target_type is None:
                        raise Exception(f"Access operation '{op}' requires a target, but no target was provided.")
                    if not t_h.contains(target_type, "text"):
                        raise Exception(f"Cannot get age from type '{target_type}'. {op} Expected 'text'.")
                    
                    if target_type != {"text"}:
                        self.target.inference(
                            v_table=v_table,
                            f_table=f_table,
                            inference_context=inference_context,
                            old_inference_value=target_type.copy(),
                            new_inference_value={"text"},
                        )

                        target_type = {"text"}

                    self.child_return_types["target"] = (target_type.copy(), self.target)
                    self.child_return_types["self"] = ({"time"}, self)
                    return {"time"}
                
                case "starts_with" | "ends_with" | "regex":
                    if target_type is None:
                        raise Exception(f"Access operation '{op}' requires a target, but no target was provided.")
                    if not t_h.contains(target_type, "text"):
                        raise Exception(f"Cannot apply operation '{op}' to type '{target_type}'. {op} Expected 'text'.")
                    
                    if target_type != {"text"}:
                        self.target.inference(
                            v_table=v_table,
                            f_table=f_table,
                            inference_context=inference_context,
                            old_inference_value=target_type.copy(),
                            new_inference_value={"text"},
                        )

                        target_type = {"text"}

                    self.child_return_types["target"] = (target_type.copy(), self.target)
                    if self.argument is not None:
                        arg_type = self.argument.check(
                            v_table=v_table, 
                            f_table=f_table, 
                            inference_context=inference_context
                        )
                        if arg_type is None:
                            raise Exception(f"Argument for operation '{op}' cannot be None.", self)
                        if not t_h.contains(arg_type, "text"):
                            raise Exception(f"Argument for operation '{op}' must contain 'text', got '{arg_type}'.")
                        if arg_type != {"text"}:
                            self.argument.inference(
                                v_table=v_table,
                                f_table=f_table,
                                inference_context=inference_context,
                                old_inference_value=arg_type.copy(),
                                new_inference_value={"text"},
                            )
                            arg_type = {"text"}
                        
                        self.child_return_types["argument"] = ({"text"}, self.argument)

                    self.child_return_types["self"] = ({"boolean"}, self)
                    return {"boolean"}

                case "unit":
                    if target_type is None:
                        raise Exception(f"Access operation '{op}' requires a target, but no target was provided.")
                    valid_target_types = {"number", "decimal", "time", "date"}
                    narrowed_target_type = t_h.narrow(target_type, valid_target_types)
                    if narrowed_target_type == set():
                        raise Exception(f"Cannot get unit of type '{target_type}'. {op} Expected number, decimal, time, or date.")
                    
                    if narrowed_target_type != target_type:
                        self.target.inference(
                            v_table=v_table,
                            f_table=f_table,
                            inference_context=inference_context,
                            old_inference_value=target_type.copy(),
                            new_inference_value=narrowed_target_type.copy(),
                        )
                        target_type = narrowed_target_type.copy()
                    
                    self.child_return_types["target"] = (target_type.copy(), self.target)
                    
                    return_types = set()
                    if t_h.is_compatible(target_type, {"number", "decimal"}):
                        return_types.add("time")
                    if t_h.is_compatible(target_type, {"time", "date"}):
                        return_types.add("number")
                    
                    self.child_return_types["self"] = (return_types.copy(), self)
                    return return_types
                
                case "now":
                    self.child_return_types["self"] = ({"date"}, self)
                    return {"date"}

                case "here":
                    self.child_return_types["self"] = ({"text"}, self)
                    return {"text"}
                
                case _:
                    raise Exception(f"Unsupported access operation '{op}'", self)
            
        except Exception as e:
            raise TraceError(node = self, cause = e)
    
    def execute(self, env: Environment) -> Any:
        try:
            target_value = self.target.execute(env) if self.target else None
            arg_value = self.argument.execute(env) if self.argument else None
            match self.operation:
                case "file_name":
                    return os.path.basename(target_value)
                case "age":
                    return os.path.getmtime(target_value)
                case "starts_with":
                    return target_value.startswith(arg_value)
                case "ends_with":
                    return target_value.endswith(arg_value)
                case "regex":
                    return re.search(arg_value, target_value) is not None
                case "length":
                    return len(target_value)
                case "first":
                    return target_value[0]
                case "last":
                    return target_value[-1]
                case "unit":
                    # This will be handled by the Unit AST node, so we can just return the value here
                    return target_value
                case "now":
                    return datetime.datetime.now()
                case "here":
                    return os.getcwd()
                case _:
                    raise TraceError(node = self, cause = f"Unsupported access operation '{self.operation}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def inference(self, v_table, f_table, inference_context, old_inference_value, new_inference_value):
        
        if "self" not in self.child_return_types:
            raise Exception(f"AccessOp inference: No type information available for access operation during inference. This node has not been checked. Node: {self}", self)
        if len(self.child_return_types["self"][0]) == 1:
            raise Exception(f"AccessOp inference: Only one possible return type '{self.child_return_types['self'][0]}' for access operation '{self.operation}'. Inference should not be necessary. Node: {self}", self)
        match self.operation:
            
            case "unit":
                remembered_return_types = self.child_return_types["self"][0]
                if old_inference_value != remembered_return_types:
                    raise Exception(
                        f"AccessOp inference: Old inference value '{old_inference_value}' does not match remembered return types '{remembered_return_types}' for access operation 'unit'. "
                        f"Something went wrong in the inference pathing. Node: {self}", self)
                if not t_h.is_compatible(new_inference_value, remembered_return_types):
                    raise Exception(
                        f"AccessOp inference: New inference value '{new_inference_value}' is not compatible with remembered return types '{remembered_return_types}' for access operation 'unit'. "
                        f"Something went wrong in the inference pathing. Node: {self}", self)

                new_target_inference = set()
                if new_inference_value == {"time"}:
                    new_target_inference = {"number", "decimal"}
                    
                elif new_inference_value == {"number"}:
                    new_target_inference = {"time", "date"}
                else:
                    raise Exception(
                        f"AccessOp inference: this It should not be possible. operation:{self.operation} new_inference_value: {new_inference_value}", self)

                self.target.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=self.child_return_types["target"][0].copy(),
                    new_inference_value=new_target_inference.copy(),
                )
                self.child_return_types["target"] = (new_target_inference.copy(), self.target)
                self.child_return_types["self"] = (new_inference_value.copy(), self)
                