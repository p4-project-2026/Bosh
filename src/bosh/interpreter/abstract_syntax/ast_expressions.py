import os
from .ast_base import *
import math




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
                list_type = t_h.make_list(elem_type)
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
            if not self.child_return_types:
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
    "TODO: Implement type checking for task calls"
    name: str
    arguments: Optional[List[ASTNode]] = None
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        try:
            signature = f_table.lookup(self.name)
            
            if len(self.arguments) != len(signature.param_types):
                raise TraceError(node = self, cause = f"Task '{self.name}' expects {len(signature.param_types)} arguments, but {len(self.arguments)} were provided.")
            for i, arg in enumerate(self.arguments):
                if i < len(signature.param_types):
                    arg_type = arg.check(v_table, f_table)
                    expected_type = signature.param_types[signature.param[i]]
                    if arg_type != expected_type and expected_type != "any":
                        raise TraceError(node = self, cause = f"Argument {i+1} of task '{self.name}' expects type '{expected_type}', but got '{arg_type}'.")
            return signature.return_type
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


@dataclass
class ListLookup(ASTNode):
    target: ASTNode
    index: ASTNode
    def  __post_init__(self):
        super().__init__()
    
        
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        try:
            self.child_return_types.clear()
            vvvprint(f"ListLookup: check: Starting type check for list lookup. Target: {self.target}, Index: {self.index}")
            index_type = self.index.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            if index_type != {"number"}:
                vvvprint(f"ListLookup: check: Index type '{index_type}' is not 'number'. Checking if it's compatible...")
                if t_h.is_unknown_type(index_type) or t_h.contains(index_type, "number"):
                    vvvprint(f"ListLookup: check: Index type '{index_type}' is compatible with 'number'. Running inference on index with new inference value 'number'...")
                    self.index.inference(v_table=v_table,
                                         f_table=f_table, 
                                         inference_context=inference_context, 
                                         old_inference_value=index_type,
                                         new_inference_value={"number"}
                                         )
                    vvvprint(f"ListLookup: check: Index type '{index_type}' inferred to 'number'.")
                    self.child_return_types["index"] = ({"number"}, self.index)
                else:
                    raise Exception(f"ListLookup: List index must be of type 'number', got '{index_type}'", self)
            else:
                vvvprint(f"ListLookup: check: Index type '{index_type}' is 'number'.")
                self.child_return_types["index"] = (index_type.copy(), self.index)
            vvvprint(f"ListLookup: check: Checking target of list lookup...")
            target_types = self.target.check(v_table=v_table,
                                             f_table=f_table,
                                             inference_context=inference_context
                                             )
            vvvprint(f"ListLookup: check: Target types: {target_types}")
            
            # check if any of the target types are can be a list type and if so, extract the element types.
            vvvprint(f"ListLookup: check: Checking if target types are compatible with list types...")
            if t_h.is_unknown_type(target_types):
                set_list_types = {UNKNOWN_LIST_TYPE}
                vvvprint(f"ListLookup: check: Target types are unknown, treating as '{set_list_types}' for inference.")
                self.target.inference(v_table=v_table,
                                      f_table=f_table,
                                      inference_context=inference_context,
                                      old_inference_value=target_types.copy(),
                                      new_inference_value=set_list_types.copy()
                                      )
                vvvprint(f"ListLookup: check: Target types inferred to '{set_list_types}'.")
                self.child_return_types["target"] = (set_list_types.copy(), self.target)
                self.child_return_types["self"] = ({UNKNOWN_TYPE}, self)
                vvvprint(f"ListLookup: check: Remembered target types for inference set to '{set_list_types}'. Remembered return type for inference set to '{UNKNOWN_TYPE}'.")
                return {UNKNOWN_TYPE}
            
            vvvprint(f"ListLookup: check: Checking if target types '{target_types}' contain any list types...")
            if not t_h.has_list_type(target_types):
                raise Exception(f"ListLookup: Type Check Failed: Cannot index into type '{target_types}', expected a list type", self)
            vvvprint(f"ListLookup: check: Target types '{target_types}' contain list types.")

            vvvprint(f"ListLookup: check: Extracting element types from target types '{target_types}' for return type of list lookup...")
            if t_h.has_non_list_type(target_types):
                vvvprint(f"ListLookup: check: Target types '{target_types}' contain non-list types. Extracting list types for inference...")
                new_target_types = t_h.get_all_list_types(target_types)
                vvvprint(f"ListLookup: check: Extracted list types: {new_target_types}")
                vvvprint(f"ListLookup: check: Running inference on target with new inference value '{new_target_types}'...")
                self.target.inference(v_table=v_table,
                                      f_table=f_table,
                                      inference_context=inference_context,
                                      old_inference_value=target_types.copy(),
                                      new_inference_value=new_target_types.copy()
                                      )
                vvvprint(f"ListLookup: check: Target types inferred to '{new_target_types}'.")
                self.child_return_types["target"] = (new_target_types.copy(), self.target)
                target_types = new_target_types
                vvvprint(f"ListLookup: check: Remembered target types for inference set to '{new_target_types}'.")
            else:
                vvvprint(f"ListLookup: check: Target types '{target_types}' contain only list types.")
                self.child_return_types["target"] = (target_types.copy(), self.target)
                vvvprint(f"ListLookup: check: Remembered target types for inference set to '{target_types}'.")  
            
            vvvprint(f"ListLookup: check: Getting list element types from target types '{target_types}' for return type of list lookup...")
            return_types = t_h.get_list_element_types(target_types)
            vvvprint(f"ListLookup: check: List element types (return types) extracted: {return_types}")
            
            vvvprint(f"ListLookup: check: Remembering return types for inference...")
            self.child_return_types["self"] = (return_types.copy(), self)
            vvvprint(f"ListLookup: check: Remembered return types for inference set to '{return_types}'.")
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
            
            vvvprint(f"ListLookup: inference: Starting inference for list lookup. Old inference value: '{old_inference_value}', New inference value: '{new_inference_value}'")
            if not self.child_return_types:
                raise Exception(f"ListLookup: inference: No type information available for list lookup during type inference {self} has not been checked.", self)
            vvvprint(f"ListLookup: inference: Current child return types: {self.child_return_types}")
            remembered_types = self.child_return_types["self"][0].copy()
            vvvprint(f"ListLookup: inference: Remembered return types for inference: {remembered_types}")

            vvvprint(f"ListLookup: inference: Checking if old inference value '{old_inference_value}' matches remembered types for list lookup...")
            if remembered_types != old_inference_value:
                raise Exception(f"ListLookup: inference: Old inference value '{old_inference_value}' does not match remembered type '{remembered_types}' for list lookup. something went wrong in type inference pathing.", self)
            vvvprint(f"ListLookup: inference: Old inference value '{old_inference_value}' matches remembered types for list lookup.")

            vvvprint(f"ListLookup: inference: Checking compatibility of new inference value '{new_inference_value}' with remembered types '{remembered_types}' for list lookup...")
            if not t_h.is_compatible(remembered_types, new_inference_value):
                raise Exception(f"ListLookup: inference: New inference value '{new_inference_value}' is incompatible with remembered type '{remembered_types}' for list lookup. something went wrong.", self)
            vvvprint(f"ListLookup: inference: New inference value '{new_inference_value}' is compatible with remembered types '{remembered_types}' for list lookup.")

            vvvprint(f"ListLookup: inference: Checking if new inference value '{new_inference_value}' narrows the remembered types '{remembered_types}' for list lookup...")
            narrowed = t_h.narrow(remembered_types, new_inference_value)
            vvvprint(f"ListLookup: inference: Narrowed types: {narrowed}")

            if narrowed == remembered_types:
                raise Exception(
                                f"ListLookup: inference path reached this node, but no narrowing occurred. "
                                f"remembered={remembered_types}, new={new_inference_value}. "
                                f"This probably means the parent passed a non-narrowing inference request.", 
                                self
                                )
            vvvprint(f"ListLookup: inference: New inference value '{new_inference_value}' narrows the remembered types for list lookup. Updating variable table and remembered types...")

            self.child_return_types["self"] = (narrowed.copy(), self)

            vvvprint(f"ListLookup: inference: Updated remembered return types for inference to '{narrowed}' for list lookup.")
            list_types = t_h.make_set_list_types(narrowed)
            vvvprint(f"ListLookup: inference: Generated list types for inference: {list_types}")
            vvvprint(f"ListLookup: inference: Running inference on target with new inference value '{list_types}'...")
            target_old_types = self.child_return_types["target"][0].copy()
            vvvprint(f"ListLookup: inference: Old target types for inference: {target_old_types}")
            self.target.inference(v_table=v_table,
                                 f_table=f_table,
                                 inference_context=inference_context,
                                 old_inference_value=target_old_types,
                                 new_inference_value=list_types.copy()
                                 )
            vvvprint(f"ListLookup: inference: Inference completed for list lookup.")
            self.child_return_types["target"] = (list_types.copy(), self.target)
            vvvprint(f"ListLookup: inference: Updated remembered target types for inference to '{list_types}' for list lookup.")                
        except Exception as e:
            raise TraceError(node = self, cause = e)    


        

                    
                        

            
        

@dataclass
class Unit(ASTNode):
    target: ASTNode
    unit_type: str

    def check(self, v_table: ScopeStack, f_table: FuncTable,  inference_context: InferenceContext) -> set[str]:
        try:
            self.child_return_types.clear()
            target_type = self.target.check(v_table=v_table,
                                             f_table=f_table,
                                             inference_context=inference_context
                                             )
            if not t_h.is_only(target_type, "number") and not t_h.is_only(target_type, "decimal"):
                possible_types = {"number", "decimal"}
                narrowed = t_h.narrow(target_type, possible_types)
                if not narrowed:
                    raise BoshTypeError(f"Cannot apply unit '{self.unit_type}' to type '{target_type}'. Expected number or decimal.", self)
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
            raise Exception("Unit inference is not supported because the return type of a unit is always 'time', so there is no need for inference. If you are seeing this error, " \
            "it means something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    
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
                raise Exception("Binary operator check failed: left or right operand has no type. left_type: {left_type}, right_type: {right_type}", self)
            
            
            op = self.operator

            
            """
                    Concatenation_case = {"text"}
                    Addition_case = {"number", "decimal"}
                    if not t_h.is_compatible(left_type, Concatenation_case) or not t_h.is_compatible(right_type, Concatenation_case):
                        # if it's not compatible with the concatenation case, it must be compatible with the addition case, otherwise it's an error.
                        if not t_h.is_compatible(left_type, Addition_case):
                            raise Exception(
                                            f"Binary operator '{op}' not supported for left type '{left_type}'. "
                                            f"Expected number, decimal, or text.",
                                            self
                                            )

                        if not t_h.is_compatible(right_type, Addition_case):
                            raise Exception(
                                            f"Binary operator '{op}' not supported for right type '{right_type}'. "
                                            f"Expected number, decimal, or text.",
                                            self
                                            )

                        # if it's compatible with the addition case, we need to narrow the types to number and decimal for the return type inference.
                        left_narrowed = t_h.narrow(left_type, Addition_case)
                        right_narrowed = t_h.narrow(right_type, Addition_case)

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

                        self.child_return_types["self"] = (return_types.copy(), self)
                        return return_types
            """
            match op:

                case "plus":
                    concatenation_case = {"text"}
                    if t_h.is_compatible(left_type, concatenation_case) or t_h.is_compatible(right_type, concatenation_case):
                        self.child_return_types["left"] = (left_type.copy(), self.left)
                        self.child_return_types["right"] = (right_type.copy(), self.right)
                        self.child_return_types["self"] = ({"text"}, self)
                        return {"text"}

                    addition_case = {"number", "decimal"}

                    if not t_h.is_compatible(left_type, addition_case):
                        raise Exception(
                                        f"Binary operator '{op}' not supported for left type '{left_type}'. "
                                        f"Expected number, decimal, or text.",
                                        self
                                        )
                    if not t_h.is_compatible(right_type, addition_case):
                        raise Exception(
                                        f"Binary operator '{op}' not supported for right type '{right_type}'. "
                                        f"Expected number, decimal, or text.",
                                        self
                                        )

                    left_narrowed = t_h.narrow(left_type, addition_case)
                    right_narrowed = t_h.narrow(right_type, addition_case)
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
                    self.child_return_types["self"] = (return_types.copy(), self)
                    return return_types 

                    
                    
                    
                    
                case "minus" | "mult" | "div":
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
                                        f"Binary operator '{op}' only supports operands of the same type. Got left type '{left_type}' and right type '{right_type}'.",
                                        self
                                        )
                    narrowe = t_h.narrow(left_type, right_type)
                    if narrowe != left_type:
                        self.left.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=left_type.copy(),
                        new_inference_value=narrowe.copy(),
                        )
                    self.child_return_types["left"] = (narrowe.copy(), self.left)
                    if narrowe != right_type:
                        self.right.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=right_type.copy(),
                        new_inference_value=narrowe.copy(),
                        )
                    self.child_return_types["right"] = (narrowe.copy(), self.right)
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
                    raise TraceError(node = self, cause = f"Unsupported operator '{op}'")










            

  
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> Any:
        try:
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
        if not self.child_return_types["self"][0]:
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
                    self.child_return_types["self"] = ({"decimal"}, self)
                    return
            
            case "mod":
                raise Exception(f"Inference for 'mod' operator is not supported because it only supports 'number' types, so there is no need for inference. "
                                f"If you are seeing this error, it means something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
            
            case "eq" | "neq" | "lt" | "gt" | "lte" | "gte":
                raise Exception(f"Inference for comparison operators is not supported because they only support operands of the same type and return 'boolean', so there is no need for inference. "
                                f"If you are seeing this error, it means something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
            
            case "or" | "and":
                raise Exception(f"Inference for logical operators is not supported because they only support 'boolean' types and return 'boolean', so there is no need for inference. "
                                f"If you are seeing this error, it means something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)

@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
            operand_type = self.operand.check(v_table, f_table)
            op = self.operator
            if op in ["-", "neg", "negative"]:
                if operand_type not in ["number", "decimal"]:
                    raise TraceError(node = self, cause = f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.")
                return operand_type
            
            elif op in ["not_", "not", "!"]:
                if operand_type != "boolean":
                    raise TraceError(node = self, cause = f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'boolean'.")
                return "boolean"
            
            elif op in ["floor", "ceiling", "round"]:
                if operand_type not in ["number", "decimal"]:
                    raise TraceError(node = self, cause = f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.")
                return "number"
            
            elif op == "exponent":
                if operand_type not in ["number", "decimal"]:
                    raise TraceError(node = self, cause = f"Unary operator 'exponent' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.")
                return "decimal"
            
            elif op == "length":
                is_list = isinstance(operand_type, str) and operand_type.startswith("list<") and operand_type.endswith(">")
                if operand_type != "text" and not is_list:
                    raise TraceError(node = self, cause = f"Unary operator 'length' not supported for type '{operand_type}'. Expected 'text' or 'list'.")
                return "number"
        
            elif op in ["first", "last"]:
                is_list = isinstance(operand_type, str) and operand_type.startswith("list<") and operand_type.endswith(">")
                if operand_type != "text" and not is_list:
                    raise TraceError(node = self, cause = f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'text' or 'list'.")
                if operand_type == "text":
                    return "text"
                else:
                    return operand_type[5:-1]
                
            else:
                raise TraceError(node = self, cause = f"Unsupported unary operator '{op}'")
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
                case "exponent":
                    return math.exp(self.operand.execute(env))
                case "round":
                    return int(round(self.operand.execute(env)))
                case _:
                    raise TraceError(node = self, cause = f"Unsupported unary operator '{self.operator}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)

@dataclass
class AccessOp(ASTNode):
    target: Optional[ASTNode]
    operation: str
    argument: Optional[ASTNode] = None
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
            target_type = self.target.check(v_table, f_table) if self.target else None
            op = self.operation

            if op == "file_name":
                if target_type != "text":
                    raise TraceError(node = self, cause = f"Cannot get file name of type '{target_type}'. Expected 'file' or 'folder'.")
                return "text"
            
            elif op == "age":
                if target_type != "text":
                    raise TraceError(node = self, cause = f"Cannot get age of type '{target_type}'. Expected 'file' or 'folder'.")
                return "number"
            
            elif op in ["starts_with", "ends_with", "regex"]:
                if target_type != "text":
                    raise TraceError(node = self, cause = f"Cannot apply operation '{op}' to type '{target_type}'. Expected 'text'.")

                if self.argument is not None:
                    arg_type = self.argument.check(v_table, f_table)
                    if arg_type != "text":
                        raise TraceError(node = self, cause = f"Argument for operation '{op}' must be of type 'text', got '{arg_type}'.")
                return "boolean"
            
            elif op == "unit":
                if target_type in ["number", "decimal"]:
                    return "time"
                elif target_type == "time":
                    return "number"
                else:
                    raise TraceError(node = self, cause = f"Time units require a numeric, date, or time target, got '{target_type}'.")
            
            elif op == "now":
                return "date"
            
            elif op == "here":
                return "text"
            
            else:
                raise TraceError(node = self, cause = f"Unsupported access operation '{op}'")
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
                    import re
                    return re.search(arg_value, target_value) is not None
                case "unit":
                    # This will be handled by the Unit AST node, so we can just return the value here
                    return target_value
                case "now":
                    import datetime
                    return datetime.datetime.now().isoformat()
                case "here":
                    return os.getcwd()
                case _:
                    raise TraceError(node = self, cause = f"Unsupported access operation '{self.operation}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)