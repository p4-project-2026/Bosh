import os
from .ast_base import *
import math




@dataclass
class NumberLiteral(ASTNode):
    value: int
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
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
        raise Exception("NumberLiteral: inference: Number literals cannot be narrowed to type '{new_inference_value}'", self)


@dataclass
class DecimalLiteral(ASTNode):
    value: float
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
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
        raise Exception("DecimalLiteral: inference: Decimal literals cannot be narrowed to type '{new_inference_value}'", self)

@dataclass
class StringLiteral(ASTNode):
    value: str
    def  __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
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
        raise Exception("StringLiteral: inference: String literals cannot be narrowed to type '{new_inference_value}'", self)


@dataclass
class InterpolatedString(ASTNode):
    parts: List[ASTNode]
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
        try:
            for part in self.parts:
                if part.check(v_table, f_table, inference_context) is None:
                    raise TraceError(node = self, cause = "Undefined variable in interpolated string")
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
        raise Exception("InterpolatedString: inference: Interpolated string literals cannot be narrowed to type '{new_inference_value}'", self)
    
@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
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
        raise Exception("BooleanLiteral: inference: Boolean literals cannot be narrowed to type '{new_inference_value}'", self)

@dataclass
class NullLiteral(ASTNode):
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
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
        raise Exception("NullLiteral: inference: Null literals cannot be narrowed to type '{new_inference_value}' because they are compatible with all types.", self)

@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
        try:
            if len(self.elements) == 0:
                self.child_return_types["element"] = ({"list<UNKNOWN>"}, self)
                return {EMPTY_LIST_TYPE}
            element_type = self.elements[0].check(v_table, f_table, inference_context)
            for elem in self.elements[1:]:
                elem_type = elem.check(v_table, f_table, inference_context)
                if elem_type != element_type:
                    raise TraceError(node = self, cause = f"List elements must all be of the same type, expected {element_type}, got {elem_type}")
            return {f"list<{element_type}>"}
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
        raise Exception("ListLiteral: inference: List literals cannot be narrowed to type '{new_inference_value}'", self)

@dataclass
class Identifier(ASTNode):
    name: str
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> set[str]:
        try:
            vvvprint(f"Identifier: check: Looking up variable '{self.name}' in variable table...")
            var_type = v_table.lookup(self.name)
            vvvprint(f"Identifier: check: Variable '{self.name}' found with type '{var_type}'")
            self.child_return_types["self"] = (var_type.copy(), self)
            vvvprint(f"Identifier: check: Remembered type for variable '{self.name}' returnes set to '{var_type}' for inference.")
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
                raise Exception(f"Identifier: inference: No remembered type found for variable '{self.name}', '{self}' has not been checked.", self)
            vvvprint(f"Identifier: inference: Current type-node pairs for variable '{self.name}': {self.child_return_types}")


            vvvprint(f"Identifier: inference: Looking up current type of variable '{self.name}' in variable table...")
            remembered_type = self.child_return_types["self"][0].copy()
            vvvprint(f"Identifier: inference: Remembered type for variable '{self.name}': {remembered_type}")
            vvvprint(f"Identifier: inference: Current type for variable '{self.name}' from variable table: {current_type}")             
            if remembered_type != current_type:
                raise Exception(f"Identifier: inference: Remembered type '{remembered_type}' for variable '{self.name}' does not match current type '{current_type}' from variable table. something went wrong in type checking or inference pathing.", self)


            vvvprint(f"Identifier: inference: Remembered type '{remembered_type}' for variable '{self.name}' matches current type '{current_type}' from variable table. Proceeding with inference...")
            current_type = v_table.lookup(self.name).copy()
            vvvprint(f"Identifier: inference: Current type for variable '{self.name}' from variable table: {current_type}")
            narrowed = new_inference_value & current_type


            vvvprint(f"Identifier: inference: New inference value '{new_inference_value}' and current type '{current_type}' for variable '{self.name}' narrowed to '{narrowed}'")
            if not narrowed:
                raise Exception(f"Identifier: inference: Cannot narrow variable '{self.name}' from type '{current_type}' to incompatible type '{new_inference_value}'.", self)
            if narrowed == current_type:
                vvvprint(f"Identifier: inference: New inference value '{new_inference_value}' does not narrow the type of variable '{self.name}' (current type: '{current_type}'). No update needed.")
                self.child_return_types["self"] = (narrowed.copy(), self)
                return
            vvvprint(f"Identifier: inference: Variable '{self.name}' can be narrowed from type '{current_type}' to '{narrowed}' based on new inference value '{new_inference_value}'. Updating variable table and remembered type for inference...")
            

            vvvprint(f"Identifier: inference: Updating variable table with new narrowed type for variable '{self.name}'...")
            v_table.bind(self.name, narrowed.copy())
            vvvprint(f"Identifier: inference: Updated type for variable '{self.name}' in variable table: {v_table.lookup(self.name)}")
            self.child_return_types["self"] = (narrowed.copy(), self.child_return_types["self"][1])
            vvvprint(f"Identifier: inference: Updated remembered type for variable '{self.name}' to '{narrowed}' for inference.")
            inference_context.mark_infered()
            vvvprint(f"Identifier: inference: Inference for variable '{self.name}' completed successfully, inference context marked as changed for a variable type update.")
            
            return
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class TaskCall(ASTNode):
    "TODO: Implement type checking for task calls"
    name: str
    arguments: Optional[List[ASTNode]] = None
    def  __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[str]:
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
    
        
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
        try:
            
            index_type = self.index.check(v_table, f_table)
            vvvprint(f"ListLookup: Target types: {target_types}, Index type: {index_type}")
            if index_type != {"number"}:
                vvvprint(f"ListLookup: Index type '{index_type}' is not 'number'.")
                if index_type == {UNKNOWN_TYPE} or {"number"} <= index_type:
                    vvvprint(f"ListLookup: Attempting to narrow index type from '{index_type}' to 'number' for list lookup...")
                    self.index.inference(v_table, f_table, index_type, {"number"})
                    vvvprint(f"ListLookup: Index type narrowed to 'number' successfully.")
                    self.child_return_types["index"] = ({"number"}, self.index)
                    vvvprint(f"ListLookup: Remembered index type 'number' for inference{self.child_return_types}.")
                else:
                    raise Exception(f"ListLookup: List index must be of type 'number', got '{index_type}'", self)
            else:
                vvvprint(f"ListLookup: Index type '{index_type}' is valid for list lookup.")
                self.child_return_types["index"] = (index_type.copy(), self.index)
                vvvprint(f"ListLookup: Remembered index type '{index_type}' for inference{self.child_return_types}.")    

            target_types = self.target.check(v_table, f_table)
            
            
            # check if any of the target types are can be a list type and if so, extract the element types.
            if target_types == {UNKNOWN_TYPE}:
                vvvprint(f"ListLookup: Target type is UNKNOWN. Attempting to narrow target type to a list type for list lookup...")
                set_list_types = set(UNKNOWN_LIST_TYPE)
                vvvprint(f"ListLookup: Narrowing target type to '{set_list_types}' for list lookup...")
                self.target.inference(v_table, f_table, target_types, set_list_types, inference_context)
                self.child_return_types["target"] = (set_list_types, self.target)
                self.child_return_types["self"] = (set(UNKNOWN_TYPE), self)
                vvvprint(f"ListLookup: Target type narrowed to '{set_list_types}' for list lookup. Remembered type-node pairs updated: {self.child_return_types}")
                return set(UNKNOWN_TYPE)
            
            if not t_h.has_list_type(target_types):
                raise Exception(f"ListLookup: Cannot index into type '{target_types}', expected a list type", self)
            
            if t_h.has_non_list_type(target_types):
                vvvprint(f"ListLookup: Warning: Some target types '{target_types}' are not list types, but at least one is. Proceeding with list lookup inference based on compatible list types.")
                new_target_types = set()
                for t in target_types:
                    if t.startswith("list<") and t.endswith(">"):
                        new_target_types.add(t)
                vvvprint(f"ListLookup: Narrowing target types to compatible list types '{new_target_types}' for list lookup inference...")
                self.target.inference(v_table, f_table, target_types, new_target_types, inference_context)
                self.child_return_types["target"] = (new_target_types, self.target)
                vvvprint(f"ListLookup: Target types narrowed to '{new_target_types}' for list lookup inference. Remembered type-node pairs updated: {self.child_return_types}")
               
            else:
                vvvprint(f"ListLookup: All target types '{target_types}' are compatible list types for list lookup inference. Remembering target types for inference...")
                self.child_return_types["target"] = (target_types, self.target)
                vvvprint(f"ListLookup: Target types '{target_types}' remembered for list lookup inference.")
            
            return_types = set()
            vvvprint(f"ListLookup: Extracting element types from target list types for list lookup inference...")
            for target_type in new_target_types:
                    if target_type.startswith("list<") and target_type.endswith(">"):
                        return_types.add(target_type[5:-1])
            vvvprint(f"ListLookup: Extracted element types from target list types: {return_types}")
            
            
            self.child_return_types["self"] = (return_types.copy(), self)
            vvvprint(f"ListLookup: Remembered return types '{return_types}' for list lookup inference.")
        
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
                new_inference_value: set[str]) -> None:
        
        try:
            
            
            vvvprint(f"ListLookup: inference: Starting inference for list lookup with old inference value '{old_inference_value}' and new inference value '{new_inference_value}'...")
            if not self.child_return_types:
                raise Exception("ListLookup: inference: No type information available for list lookup during type inference {self} has not been checked.", self)
            vvvprint(f"ListLookup: inference: Current type-node pairs for list lookup: {self.child_return_types}")
            remembered_types = self.child_return_types["self"][0].copy()
            vvvprint(f"ListLookup: inference: Remembered types for list lookup: {remembered_types}")

            vvvprint(f"ListLookup: inference: Checking if infrance pathing is following the correct path for list lookup inference...")
            if remembered_types != old_inference_value:
                raise Exception(f"ListLookup: inference: Old inference value '{old_inference_value}' does not match remembered type '{remembered_types}' for list lookup. something went wrong in type inference pathing.", self)
            vvvprint(f"ListLookup: inference: Old inference value '{old_inference_value}' matches remembered type '{remembered_types}' for list lookup. Proceeding with inference...")


            narowed = remembered_types & new_inference_value
            if not narowed:
                raise Exception(f"ListLookup: inference: New inference value '{new_inference_value}' is incompatible with remembered type '{remembered_types}' for list lookup. something went wrong in type inference.", self)
            vvvprint(f"ListLookup: inference: New inference value '{new_inference_value}' is compatible with remembered type '{remembered_types}' for list lookup. Narrowed type: {narowed}") 
            
            vvvprint(f"ListLookup: inference: Looking up current type of variable in variable table for list lookup inference...")
            curent_types_list_from = v_table.lookup(self.target.name)
            vvvprint(f"ListLookup: inference: Current types for variable '{self.target.name}' from variable table: {curent_types_list_from}")                        

            curent_types = set()
            vvvprint(f"ListLookup: inference: Extracting element types from current list types...")
            for current_type in curent_types_list_from:
                if current_type.startswith("list<") and current_type.endswith(">"):
                    curent_types.add(current_type[5:-1])
                else:
                    raise Exception(f"ListLookup: inference: Current type '{current_type}' for variable '{self.target.name}' is not a list type. something went wrong in type checking.", self)
            vvvprint(f"ListLookup: inference: Extracted element types from current list types: {curent_types}")

            vvvprint(f"ListLookup: inference: Checking compatibility of new inference value '{new_inference_value}' with current element types '{curent_types}' for list lookup...")
            new_narrowed = new_inference_value & curent_types
            vvvprint(f"ListLookup: inference: New narrowed types based on new inference value: {new_narrowed}")

            vvvprint(f"ListLookup: inference: Checking if new narrowed types are compatible with current element types for list lookup...")
            if not new_narrowed:
                raise Exception(f"ListLookup: inference: New inference value '{new_inference_value}' is incompatible with current types '{curent_types}' for list lookup.", self)
            vvvprint(f"ListLookup: inference: New inference value '{new_inference_value}' is compatible with current types '{curent_types}' for list lookup.")

            vvvprint(f"ListLookup: inference: Checking if new narrowed types are the same as current element types for list lookup...")
            if new_narrowed == curent_types:
                vvvprint(f"ListLookup: inference: New inference value '{new_inference_value}' does not narrow the current types for list lookup (current types: '{curent_types}'). No update needed.")
                self.type_node_pairs[0] = (set(f"list<{t}>" for t in new_narrowed), self.type_node_pairs[0][1])
                return
            

            vvvprint(f"ListLookup: inference: New inference value '{new_inference_value}' narrows the current types for list lookup. Updating variable table and remembered types...")
            new_list_types = set()
            for new_type in new_narrowed:
                new_list_types.add(f"list<{new_type}>")
            vvvprint(f"ListLookup: inference: Updating variable '{self.type_node_pairs[0][1].name}' in variable table to new inferred types '{new_list_types}'...")
            v_table.bind(self.type_node_pairs[0][1].name, new_list_types)
            vvvprint(f"ListLookup: inference: Updated variable '{self.type_node_pairs[0][1].name}' in variable table to new inferred type '{new_list_types}' based on new inference value '{new_inference_value}'.")
            self.type_node_pairs[0] = (new_list_types, self.type_node_pairs[0][1])
            inference_context.mark_infered()
            vvvprint(f"ListLookup: inference: Updated type-node pair for list lookup to new inferred type '{new_list_types}'.")


                
        except Exception as e:
            raise TraceError(node = self, cause = e)    


        vvvprint(f"ListLookup: inference: Starting inference for list lookup with old inference value '{old_inference_value}' and new inference value '{new_inference_value}'...")
        if not self.type_node_pairs:
            raise Exception("ListLookup: inference: No type information available for list lookup during type inference", self)
        vvvprint(f"ListLookup: Current type-node pairs: {self.type_node_pairs}")
    
        if old_inference_value != self.type_node_pairs[0][0]:
            vvvprint(f"ListLookup: inference: Old inference value '{old_inference_value}' does not match remembered type '{self.type_node_pairs[0][0]}'. No update performed.")
            if self.type_node_pairs[0][0].issubset(old_inference_value):
                vvvprint(f"ListLookup: inference: Remembered type '{self.type_node_pairs[0][0]}' is a subset of old inference value '{old_inference_value}'. No update performed.")
                if new_inference_value.issubset(self.type_node_pairs[0][0]):
                    vvvprint(f"ListLookup: inference: New inference value '{new_inference_value}' is a subset of remembered type '{self.type_node_pairs[0][0]}'. No update performed.")
                    new_list_types = set()
                    for new_type in new_inference_value:
                        new_list_types.add(f"list<{new_type}>")
                    v_table.bind(self.type_node_pairs[0][1].name, new_list_types)
                    vvvprint(f"ListLookup: inference: Updated variable '{self.type_node_pairs[0][1].name}' in variable table to new inferred type '{new_list_types}' based on new inference value '{new_inference_value}'.")
                    self.type_node_pairs[0] = (new_list_types, self.type_node_pairs[0][1])
                    vvvprint(f"ListLookup: inference: Updated type-node pair for list lookup to new inferred type '{new_list_types}'.")
                    return
            raise Exception(f"ListLookup: inference: {self.type_node_pairs[0][0]} is not compatible with old inference values '{old_inference_value}' and new inference value '{new_inference_value}'.", self)
            return
        vvvprint(f"ListLookup: inference: Old inference value matches remembered type. Updating variable '{self.type_node_pairs[0][1].name}' in variable table to new inference value '{new_inference_value}'...")
        new_list_types = set()
        for new_type in new_inference_value:
            new_list_types.add(f"list<{new_type}>")
        v_table.bind(self.type_node_pairs[0][1].name, new_list_types)
        vvvprint(f"ListLookup: inference: Updated variable '{self.type_node_pairs[0][1].name}' in variable table to new inferred type '{new_list_types}' based on new inference value '{new_inference_value}'.")
        self.type_node_pairs[0] = (new_list_types, self.type_node_pairs[0][1])
        vvvprint(f"ListLookup: inference: Updated type-node pair for list lookup to new inferred type '{new_list_types}'.")

                    
                        

            
        

@dataclass
class Unit(ASTNode):
    target: ASTNode
    unit_type: str

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
            

            target_type = self.target.check(v_table, f_table)
            if target_type not in ["number", "decimal"]:
                if target_type == "UNKNOWN":
                    raise TraceError(node = self, cause = f"Cannot apply unit '{self.unit_type}' to type '{target_type}'. Expected number or decimal.")
            raise BoshTypeError(f"Cannot apply unit '{self.unit_type}' to type '{target_type}'. Expected number or decimal.", self)
        return "time"
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

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
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
                    raise TraceError(node = self, cause = f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'")

            elif op in ["eq", "neq"]:
                numeric_eq = (left_type in ["number", "decimal"] and right_type in ["number", "decimal"])
                null_eq = (left_type == "null" or right_type == "null")
                if left_type != right_type and not numeric_eq and not null_eq:
                    raise TraceError(node = self, cause = f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'")
                return "boolean"
            
            elif op in ["or", "and"]:
                if left_type != "boolean" or right_type != "boolean":
                    raise TraceError(node = self, cause = f"Logical operator '{op}' requires boolean operands, got '{left_type}' and '{right_type}'")
                return "boolean"
            
            elif op in ["lt", "gt", "gte", "lte"]:
                if left_type not in ["number", "decimal", "date", "time"] or right_type not in ["number", "decimal", "date", "time"]:
                    raise TraceError(node = self, cause = f"Relational operator '{op}' requires numeric or temporal operands, got '{left_type}' and '{right_type}'.")
                return "boolean"
            
            else:
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