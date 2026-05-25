import os
from unittest import case
from .ast_base import *
import math
import datetime
import re

@dataclass
class Type(ASTNode):
    name: str
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking type '{self.name}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Type '{self.name}' checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        log_case.set("success")
        return {self.name}
    

    @logged(
        start=lambda self, env: (
            f"Executing type '{self.name}'..."
        ),
        success={
            "success": lambda self, env: (
                f"Type '{self.name}' executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> str:
        log_case.set("success")
        return self.name
    

@dataclass
class NumberLiteral(ASTNode):
    value: int
    def  __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking number literal '{self.value}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Number literal '{self.value}' checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            self.child_return_types.clear()
            self.child_return_types["self"] = ({"number"}, self) # remember the return type for inference
            log_case.set("success")
            return {"number"}
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing number literal '{self.value}'..."
        ),
        success={
            "success": lambda self, env: (
                f"Number literal '{self.value}' executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> int:
        log_case.set("success")
        return self.value


@dataclass
class DecimalLiteral(ASTNode):
    value: float
    def  __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking decimal literal '{self.value}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Decimal literal '{self.value}' checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            self.child_return_types.clear()
            self.child_return_types["self"] = ({"decimal"}, self) # remember the return type for inference
            log_case.set("success")
            return {"decimal"}
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing decimal literal '{self.value}'..."
        ),
        success={
            "success": lambda self, env: (
                f"Decimal literal '{self.value}' executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> float:
        log_case.set("success")
        return self.value

        
@dataclass
class StringLiteral(ASTNode):
    value: str
    def  __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking string literal '{self.value}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"String literal '{self.value}' checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            self.child_return_types.clear()
            self.child_return_types["self"] = ({"text"}, self) # remember the return type for inference
            log_case.set("success")
            return {"text"}
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing string literal '{self.value}'..."
        ),
        success={
            "success": lambda self, env: (
                f"String literal '{self.value}' executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> str:
        log_case.set("success")
        return self.value
        

@dataclass
class InterpolatedString(ASTNode):
    parts: List[ASTNode]
    def  __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking interpolated string with parts '{self.parts}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Interpolated string checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            for i, part in enumerate(self.parts):
                if part.check(v_table, f_table, inference_context) is None:
                    raise TraceError(node = self, cause = "Undefined variable in interpolated string")
                self.child_return_types[f"part_{i}"] = (part.child_return_types["self"][0].copy(), part) # remember the type of each part for inference
            self.child_return_types["self"] = ({"text"}, self) # remember the return type for inference
            log_case.set("success")
            return {"text"}
        except Exception as e:
            raise TraceError(node = self, cause = e)

    @logged(
        start=lambda self, env: (
            f"Executing interpolated string with parts '{self.parts}'..."
        ),
        success={
            "success": lambda self, env: (
                f"Interpolated string executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> str:
        result = ""
        for i, part in enumerate(self.parts):
            value = part.execute(env)
            if self.child_return_types[f"part_{i}"][0] == {"boolean"}:
                value = f_h.string_format_bool(value)
            result += str(value)
        log_case.set("success")
        return result
    
        
@dataclass
class DateLiteral(ASTNode):
    value: str
    def  __post_init__(self):
        super().__init__() 


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking date literal with value '{self.value}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Date literal checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            self.child_return_types.clear()
            self.child_return_types["self"] = ({"date"}, self) # remember the return type for inference
            log_case.set("success") 
            return {"date"}
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing date literal with value '{self.value}'..."
        ),
        success={
            "success": lambda self, env: (
                f"Date literal executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> datetime.datetime:
        try:
            result = datetime.datetime.fromisoformat(self.value)
            log_case.set("success")
            return result
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    def  __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking boolean literal with value '{self.value}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Boolean literal checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            self.child_return_types.clear()
            self.child_return_types["self"] = ({"boolean"}, self) # remember the return type for inference
            log_case.set("success")
            return {"boolean"}
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing boolean literal with value '{self.value}'..."
        ),
        success={
            "success": lambda self, env: (
                f"Boolean literal executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> bool:
        log_case.set("success")
        return self.value


@dataclass
class NullLiteral(ASTNode):
    def  __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking null literal..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Null literal checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            self.child_return_types.clear()
            self.child_return_types["self"] = ({"null"}, self) # remember the return type for inference
            log_case.set("success")
            return {"null"}
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing null literal..."
        ),
        success={
            "success": lambda self, env: (
                f"Null literal executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        log_case.set("success")
        return None
        

@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]
    def  __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking list literal with elements '{self.elements}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"List literal checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
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
            
            list_type = t_h.make_set_list_types(element_type)


            self.child_return_types["element"] = (element_type.copy(), self.elements[0])# all elements have the same type, so we can just use the first one to remember the type for inference. this node will not be infered itself, it's just for consistency and potential future use.
            self.child_return_types["self"] = (list_type.copy(), self) # remember the return type for inference
            log_case.set("success")
            return list_type
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing list literal with elements '{self.elements}'..."
        ),
        success={
            "success": lambda self, env: (
                f"List literal executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> List[Any]:
        try:
            log_case.set("success")
            return [elem.execute(env) for elem in self.elements]
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Identifier(ASTNode):
    name: str
    def  __post_init__(self):
        super().__init__()
    
    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking identifier '{self.name}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Identifier '{self.name}' checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            self.child_return_types.clear()
            var_type = v_table.lookup(self.name)
            self.child_return_types["self"] = (var_type.copy(), self)

            log_case.set("success")
            return var_type
        except Exception as e:
            raise TraceError(node = self, cause = e)

    @logged(
        start=lambda self, env: (
            f"Executing identifier '{self.name}'..."
        ),
        success={
            "success": lambda self, env, result: (
                f"Identifier '{self.name}' executed successfully. Result: {result}"
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> Any:
        try:
            value = env.lookup_variable(self.name)
            if value is None:
                raise Exception(f"Identifier '{self.name}' is defined, but has not been assigned a value.", self)
            log_case.set("success", result=value)
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e)

    @logged(
        start=lambda self, v_table, f_table, inference_context, old_inference_value, new_inference_value: (
            f"Attempting type inference for identifier '{self.name}'. Old inference value: '{old_inference_value}', New inference value: '{new_inference_value}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, old_inference_value, new_inference_value, new_type: (
                f"Type inference for identifier '{self.name}' completed successfully. Variable type updated to '{new_type}'."
            )
        }
    )    
    def inference(
        self,
        v_table: ScopeStack,
        f_table: FuncTable,
        inference_context: InferenceContext,
        old_inference_value: set[str],
        new_inference_value: set[str],
        log_case: LogCase
    ) -> None:
        try:
            vvvprint(f"Identifier: inference: Inferring type for identifier '{self.name}'. Old inference value: '{old_inference_value}', New inference value: '{new_inference_value}'...")

            if "self" not in self.child_return_types:
                raise Exception(f"Identifier: inference: No type information available for variable '{self.name}' during type inference. {self} has not been checked.", self)

            remembered_type = self.child_return_types["self"][0].copy()

            if remembered_type != old_inference_value:
                raise Exception(f"Identifier: inference: Old inference value '{old_inference_value}' does not match remembered type '{remembered_type}' for variable '{self.name}'. something went wrong in type inference pathing.", self)

            current_type = v_table.lookup(self.name).copy()
            if not t_h.is_compatible(current_type, new_inference_value):
                raise Exception(f"Identifier: inference: New inference value '{new_inference_value}' is incompatible with current type '{current_type}' for variable '{self.name}'. something went wrong in type inference.", self)

            narrowed = t_h.narrow(current_type, new_inference_value)
            if narrowed == current_type:
                raise Exception(
                    f"Identifier: inference path reached this node, but no narrowing occurred. "
                    f"current={current_type}, new={new_inference_value}. "
                    f"This probably means the parent passed a non-narrowing inference request.",
                    self
                )


            v_table.bind(self.name, narrowed.copy())
            self.child_return_types["self"] = (narrowed.copy(), self)
            inference_context.mark_infered()
            log_case.set("success", new_type=narrowed.copy())
            return
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class TaskCall(ASTNode):
    name: str
    arguments: Optional[List[ASTNode]] = None
    def  __post_init__(self):
        super().__init__()

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking task call '{self.name}' with arguments '{self.arguments}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, return_type: (
                f"Task call '{self.name}' checked successfully with return type '{return_type}'."
            )
        }    
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> Optional[set[str]]:
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

            if signature.return_type is not None:
                self.child_return_types["self"] = (signature.return_type.copy(), self)
                log_case.set("success", return_type=signature.return_type.copy())
                return signature.return_type.copy()
            log_case.set("success", return_type=None)
            return None
        except Exception as e:
            raise TraceError(node = self, cause = e)

    @logged(
        start=lambda self, env: (
            f"Executing task call '{self.name}' with arguments '{self.arguments}'..."
        ),
        success={
            "return_val": lambda self, env, return_val: (
                f"Task call '{self.name}' executed successfully with return value '{return_val}'."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> Any:
        try:
            task_func = env.get_function(self.name)

            values : List[Any] = []
            for i in range(len(task_func.parameters)):
                values.append(self.arguments[i].execute(env))
            
            env.enter_function_scope(self.name)
            for i in range(len(task_func.parameters)):
                param_name = task_func.parameters[i]
                param_value = values[i]
                env.assign_variable(param_name, param_value)
            
            result = task_func.body.execute(env)
            env.exit_scope()
            log_case.set("return_val", return_val=result)
            return result
        except TraceError as e:
            raise TraceError(node = self,cause = e)



@dataclass
class ListLookup(ASTNode):
    target: ASTNode
    index: ASTNode
    def  __post_init__(self):
        super().__init__()
    
    
    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking list lookup on target '{self.target}' with index '{self.index}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, return_type: (
                f"List lookup checked successfully with return type '{return_type}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
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
            log_case.set("success", return_type=return_types.copy())
            return return_types
        except Exception as e:
            raise TraceError(node = self, cause = e)
    
    @logged(
        start=lambda self, env: (
            f"Executing list lookup on target '{self.target}' with index '{self.index}'..."
        ),
        success={
            "success": lambda self, env, result: (
                f"List lookup executed successfully. Result: {result}"
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> Any:
        try:
            target_value = self.target.execute(env)
            

            index_value = self.index.execute(env)
            result = target_value[int(index_value)]
            log_case.set("success", result=result)
            return result
        except Exception as e:
            raise TraceError(node = self, cause = e)
    @logged(
        start=lambda self, v_table, f_table, inference_context, old_inference_value, new_inference_value: (
            f"Attempting type inference for list lookup. Old inference value: '{old_inference_value}', New inference value: '{new_inference_value}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, old_inference_value, new_inference_value: (
                f"Type inference for list lookup completed successfully. Target type updated to '{self.child_return_types['target'][0]}', Return type updated to '{self.child_return_types['self'][0]}'."
            )
        }
    )    
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str],
                log_case: LogCase
                ) -> None:
        try:
            
            if "self" not in self.child_return_types:
                raise Exception(f"ListLookup: inference: No type information available for list lookup during type inference {self} has not been checked.", self)
            
            remembered_types = self.child_return_types["self"][0].copy()

            if remembered_types != old_inference_value:
                raise Exception(f"ListLookup: inference: Old inference value '{old_inference_value}' does not match remembered type '{remembered_types}' for list lookup. something went wrong in type inference pathing.", self)
            if not t_h.is_compatible(remembered_types, new_inference_value):
                raise Exception(f"list lookup inference: New inference value '{new_inference_value}' is incompatible with current type '{remembered_types}' for list lookup. something went wrong in type inference.", self)

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
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)

@dataclass
class TextLookup(ASTNode):
    target: ASTNode
    index: ASTNode
    def  __post_init__(self):
        super().__init__()

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking text lookup on target '{self.target}' with index '{self.index}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Text lookup checked successfully with return type '{self.child_return_types['self'][0]}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            if self.target is None or self.index is None:
                raise Exception("TextLookup: Target and index cannot be None")
            
            target_type = self.target.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            if target_type is None:
                raise Exception("TextLookup: Target of text lookup cannot be of type 'None'")
            
            if not t_h.contains(target_type, "text"):
                raise Exception("TextLookup: Target of text lookup must be of type 'text'")

            if target_type != {"text"}:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=target_type.copy(),
                    new_inference_value={"text"}
                    )
                target_type = {"text"}

            index_type = self.index.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            if index_type is None:
                raise Exception("TextLookup: Index of text lookup cannot be of type 'None'")
            
            if not t_h.contains(index_type, "number"):
                raise Exception("TextLookup: Index of text lookup must be of type 'number'")

            if index_type != {"number"}:
                self.index.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=index_type.copy(),
                    new_inference_value={"number"}
                    )
                index_type = {"number"}

            self.child_return_types["target"] = (target_type.copy(), self.target)
            self.child_return_types["index"] = (index_type.copy(), self.index)
            self.child_return_types["self"] = ({"text"}, self)

            log_case.set("success")

            return {"text"}
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> Any:
        try:
            target_value = self.target.execute(env)
            key_value = self.index.execute(env)
            return target_value[int(key_value)]
        except Exception as e:
            raise TraceError(node = self, cause = e)

@dataclass
class Unit(ASTNode):
    value: ASTNode
    unit_type: str
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking unit '{self.unit_type}' applied to value '{self.value}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Unit '{self.unit_type}' checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable,  inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            self.child_return_types.clear()
            value_type = self.value.check(v_table=v_table,
                                             f_table=f_table,
                                             inference_context=inference_context
                                             )
            
            possible_types = {"number", "decimal"}
            if not t_h.is_compatible(value_type, possible_types):
                raise BoshTypeError(f"Cannot apply unit '{self.unit_type}' to type '{value_type}'. Expected number or decimal.", self)
            
            narrowed = t_h.narrow(value_type, possible_types)
            
            if narrowed != value_type:
                self.value.inference(v_table=v_table,
                                      f_table=f_table,
                                      inference_context=inference_context,
                                      old_inference_value=value_type.copy(),
                                      new_inference_value=narrowed.copy()
                                      )
                
                value_type = narrowed.copy()

            self.child_return_types["value"] = (value_type.copy(), self.value)
            self.child_return_types["self"] = ({"time"}, self) # the return type of a unit is always time, so we can just set it directly without needing to remember it for inference.
            log_case.set("success")
            return {"time"}
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> Any:
        try:
            target_value = self.value.execute(env)
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
class TypeCast(ASTNode):
    target: ASTNode
    target_type: Type
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking type cast for node '{self.__class__.__name__}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Type cast checked successfully: from type '{self.child_return_types['target'][0]}' to type '{self.child_return_types['self'][0]}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            
            self.child_return_types.clear()
            original_type = self.target.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )

            if original_type is None:
                raise Exception("TypeCast: Target of type cast cannot be of type 'None'", self)
            target_type_name = self.target_type.check(
                v_table=v_table,
                f_table=f_table,
                inference_context=inference_context
            )

            target_type = next(iter(target_type_name))
            if target_type not in ["number", "decimal", "text", "boolean", "date"]:
                raise Exception(f"Unsupported target type for type cast: '{target_type}'", self)
            match target_type:
                case "text":
                    valid_target_types = {"number", "decimal", "boolean", "date", "text"}
                    return_type = {"text"}
            
                case "number":
                    valid_target_types = {"number", "decimal", "text"}
                    return_type = {"number"}
                
                case "decimal":
                    valid_target_types = {"number", "decimal", "text"}
                    return_type = {"decimal"}

                case "boolean":
                    valid_target_types = {"boolean", "text"}
                    return_type = {"boolean"}

                case "date":
                    valid_target_types = {"date", "text"}
                    return_type = {"date"}

                case _:
                    raise Exception(f"Unsupported target type for type cast: '{self.target_type}'")
                
            narrowed_type = t_h.narrow(original_type, valid_target_types)
            if narrowed_type == set():
                raise Exception(f"Cannot cast from '{original_type}' to '{self.target_type}'", self)
            
            if narrowed_type != original_type:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=original_type.copy(),
                    new_inference_value=narrowed_type.copy()
                )

                original_type = narrowed_type.copy()
            
            self.child_return_types["target"] = (original_type.copy(), self.target)
            self.child_return_types["self"] = (return_type.copy(), self)
            log_case.set("success")
            return return_type
                
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing type cast for node '{self.__class__.__name__}'..."
        ),
        success={
            "success": lambda self, env: (
                f"Type cast executed successfully. Result type: '{self.child_return_types['self'][0]}'."
            )
        }
    )   
    def execute(self, env: Environment, log_case: LogCase) -> Any:
        try:
            value = self.target.execute(env)
            target_type = self.target_type.execute(env)
            match target_type:
                case "number":
                    log_case.set("success")
                    return int(value)
                case "decimal":
                    log_case.set("success")
                    return float(value)
                case "text":
                    if self.child_return_types["target"][0] == {"boolean"}:
                        return "true" if value else "false"
                    log_case.set("success")
                    return str(value)
                case "boolean":
                    log_case.set("success")
                    return bool(value)
                case "date":
                    if self.child_return_types["target"][0] == {"text"}:
                            log_case.set("success")
                            return datetime.datetime.fromisoformat(value)
                    log_case.set("success")
                    return value  # if it's already a date, just return it
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
    
    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking binary operation '{self.operator}' with left operand '{self.left}' and right operand '{self.right}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Binary operation '{self.operator}' checked successfully with return type '{self.child_return_types['self'][0]}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:

            self.child_return_types.clear()
            left_type = self.left.check(
                v_table=v_table,
                f_table=f_table,
                inference_context=inference_context
            )

            
            right_type = self.right.check(
                v_table=v_table, 
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
                    
                case  "plus" | "minus" | "mult" | "div" | "pow" | "mod":
                    valid_input_types = {"number", "decimal", "date", "time"}
                    if left_type is None:
                        raise Exception(
                            f"Binary operator '{op}' check failed: left operand has no type.",
                            self
                        )
                    
                    if right_type is None:
                        raise Exception(
                            f"Binary operator '{op}' check failed: right operand has no type.",
                            self
                        )
                    
                    if not t_h.is_compatible(left_type, valid_input_types):
                        raise Exception(
                            f"Binary operator '{op}' not supported for left type '{left_type}'. "
                            f"Expected number or decimal."
                        )

                    if not t_h.is_compatible(right_type, valid_input_types):
                        raise Exception(
                            f"Binary operator '{op}' not supported for right type '{right_type}'. "
                            f"Expected number or decimal."
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
                        left_type = left_narrowed.copy()

                    if right_narrowed != right_type:
                        self.right.inference(
                            v_table=v_table,
                            f_table=f_table,
                            inference_context=inference_context,
                            old_inference_value=right_type.copy(),
                            new_inference_value=right_narrowed.copy(),
                        )
                        right_type = right_narrowed.copy()

                    self.child_return_types["left"] = (left_type.copy(), self.left)
                    self.child_return_types["right"] = (right_type.copy(), self.right)
                    return_types = set()

                    

                    if t_h.contains(right_type, "number") and t_h.contains(left_type, "number"):

                        return_types.add("number")
                    
                    if t_h.contains(right_type, "decimal") and t_h.is_compatible(left_type, t_h.NUMERIC_TYPES) \
                        or (t_h.contains(left_type, "decimal") and t_h.is_compatible(right_type, t_h.NUMERIC_TYPES)):

                        return_types.add("decimal")
                    
                    if t_h.contains(right_type, "time") and t_h.is_compatible(left_type, t_h.NUMERIC_TYPES) \
                        or (t_h.contains(left_type, "time") and t_h.is_compatible(right_type, t_h.NUMERIC_TYPES)):

                        return_types.add("time")

                    if op in ["plus", "minus"] and t_h.contains(right_type, "time") and t_h.contains(left_type, "time"):

                        return_types.add("time")

                    if op in ["plus", "minus"] and((t_h.contains(right_type, "date") and t_h.contains(left_type, "time")) \
                        or (t_h.contains(left_type, "date") and t_h.contains(right_type, "time"))):

                        return_types.add("date")

                    if op == "minus" and t_h.contains(right_type, "date") and t_h.contains(left_type, "date"):

                        return_types.add("time")
                    
                    if return_types == set():
                        raise Exception(
                                        f"Binary operator '{op}' does not support the combination of left type '{left_type}' and right type '{right_type}'."
                                        )
                    
                    self.child_return_types["self"] = (return_types.copy(), self)
                    log_case.set("success")
                    return return_types

                    
                case "eq" | "neq":
                    if left_type == right_type:
                        self.child_return_types["left"] = (left_type.copy(), self.left)
                        self.child_return_types["right"] = (right_type.copy(), self.right)
                        self.child_return_types["self"] = ({"boolean"}, self)
                        log_case.set("success")
                        return {"boolean"}
                    if not t_h.is_compatible(left_type, right_type):
                        if not (t_h.is_compatible(left_type, t_h.NUMERIC_TYPES) and t_h.is_compatible(right_type, t_h.NUMERIC_TYPES)):
                            raise Exception(
                                f"Binary operator '{op}' only supports operands of compatible types. "
                                f"Got left type '{left_type}' and right type '{right_type}'."
                                )
                        narrowed_left = t_h.narrow(left_type, t_h.NUMERIC_TYPES)
                        narrowed_right = t_h.narrow(right_type, t_h.NUMERIC_TYPES)
                    else:
                        narrowed_right = narrowed_left = t_h.narrow(left_type, right_type)
                    if narrowed_left != left_type:
                        new_left_type = narrowed_left.copy()
                        

                        self.left.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=left_type.copy(),
                        new_inference_value=new_left_type.copy(),
                        )

                        left_type = new_left_type.copy()

                    self.child_return_types["left"] = (left_type.copy(), self.left)

                    if narrowed_right != right_type:
                        new_right_type = narrowed_right.copy()


                        self.right.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=right_type.copy(),
                        new_inference_value=new_right_type.copy(),
                        )
                        
                        right_type = new_right_type.copy()

                    self.child_return_types["right"] = (right_type.copy(), self.right)
                    self.child_return_types["self"] = ({"boolean"}, self)
                    log_case.set("success")
                    return {"boolean"}

                case "lt" | "gt" | "loet" | "goet":
                    if left_type == right_type:
                        self.child_return_types["left"] = (left_type.copy(), self.left)
                        self.child_return_types["right"] = (right_type.copy(), self.right)
                        self.child_return_types["self"] = ({"boolean"}, self)
                        log_case.set("success")
                        return {"boolean"}
                    if not t_h.is_compatible(left_type, right_type):
                        raise Exception(
                                        f"Binary operator '{op}' only supports operands of compatible types. "
                                        f"Got left type '{left_type}' and right type '{right_type}'.",
                                        )
                    
                    narrowed = t_h.narrow(left_type, right_type)
                    if narrowed != left_type:
                        new_left_type = narrowed.copy()
                        
                        self.left.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=left_type.copy(),
                        new_inference_value=new_left_type.copy(),
                        )

                        left_type = new_left_type.copy()

                    self.child_return_types["left"] = (left_type.copy(), self.left)

                    if narrowed != right_type:
                        new_right_type = narrowed.copy()
                        

                        self.right.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=right_type.copy(),
                        new_inference_value=new_right_type.copy(),
                        )
                        
                        right_type = new_right_type.copy()

                    self.child_return_types["right"] = (right_type.copy(), self.right)
                    self.child_return_types["self"] = ({"boolean"}, self)
                    log_case.set("success")
                    return {"boolean"}
                
                case "eq_type" | "neq_type":
                    self.child_return_types["left"] = (left_type.copy(), self.left)
                    self.child_return_types["right"] = (right_type.copy(), self.right)
                    self.child_return_types["self"] = ({"boolean"}, self)
                    log_case.set("success")
                    return {"boolean"}

                case "or" | "and":
                    valid_input_types = {"boolean"}
                    if not t_h.is_compatible(left_type, valid_input_types):
                        raise Exception(
                            f"Binary operator '{op}' not supported for left type '{left_type}'. "
                            f"Expected boolean."
                        )
                    
                    if not t_h.is_compatible(right_type, valid_input_types):
                        raise Exception(
                            f"Binary operator '{op}' not supported for right type '{right_type}'. "
                            f"Expected boolean."
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
                    log_case.set("success")
                    return {"boolean"}

                case _:
                    raise Exception(f"Binary operator '{op}' is not supported", self)

        except Exception as e:
            raise TraceError(node = self, cause = e)



    @logged(
        start=lambda self, env: (
            f"Executing binary operation '{self.operator}' with left operand '{self.left}' and right operand '{self.right}'..."
        ),
        success={
            "success": lambda self, env, result: (
                f"Binary operation '{self.operator}' executed successfully. Result: {result}"
            )   
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> Any:
        try:
            left_val = self.left.execute(env)
            right_val = self.right.execute(env)
            match self.operator:
                case "plus":
                    # datetime + milliseconds
                    if self.child_return_types["left"][0] == {"date"} and self.child_return_types["right"][0] == {"time"}:
                        result = left_val + datetime.timedelta(milliseconds=right_val)
                        log_case.set("success", result=result)
                        return result

                    # milliseconds + datetime -> swap
                    if self.child_return_types["left"][0] == {"time"} and self.child_return_types["right"][0] == {"date"}:
                        result = right_val + datetime.timedelta(milliseconds=left_val)
                        log_case.set("success", result=result)
                        return result
                    # string concatenation
#                    if isinstance(left_val, str) or isinstance(right_val, str):
#                        if isinstance(left_val, bool):
#                            left_val = "true" if left_val else "false"
#                        return str(left_val) + str(right_val)
                    # fallback to python add (may raise)
                    result = left_val + right_val
                    log_case.set("success", result=result)
                    return result
                case "minus":
                    if self.child_return_types["left"][0] == {"date"} and self.child_return_types["right"][0] == {"time"}:
                        result = left_val - datetime.timedelta(milliseconds=right_val)
                        log_case.set("success", result=result)
                        return result
                    # numeric subtraction
                    result = left_val - right_val
                    log_case.set("success", result=result)
                    return result
                case "mult":
                    result = left_val * right_val
                    log_case.set("success", result=result)
                    return result
                case "div":
                    result = left_val / right_val
                    log_case.set("success", result=result)
                    return result
                case "mod":
                    result = left_val % right_val
                    log_case.set("success", result=result)
                    return result
                case "pow":
                    result = left_val ** right_val
                    log_case.set("success", result=result)
                    return result
                case "eq":
                    if type(left_val) != type(right_val):
                        if (type(left_val) in [int, float] and type(right_val) in [int, float]):
                            pass
                        else:
                            log_case.set("success", result=False)
                            return False
                    result = left_val == right_val
                    log_case.set("success", result=result)
                    return result
                case "neq":
                    if type(left_val) != type(right_val):
                        if (type(left_val) in [int, float] and type(right_val) in [int, float]):
                            pass
                        else:
                            result = True
                            log_case.set("success", result=result)
                            return result
                    result = left_val != right_val
                    log_case.set("success", result=result)
                    return result
                case "eq_type" | "neq_type":

                    
                    if right_val in ["folder", "file"]:
                        if t_h.contains(self.child_return_types["left"][0], "text"):
                            if right_val == "folder":
                                result = os.path.isdir(left_val)
                                log_case.set("success", result=result)
                                return result
                            else:
                                result = os.path.isfile(left_val)
                                log_case.set("success", result=result)
                                return result
                        else:
                            raise TraceError(node = self, cause = f"Left operand must be a string when comparing to 'file' or 'folder', got '{type(left_val).__name__}'")
                    if self.operator == "eq_type":
                        result = python_type_to_bosh_type(type(left_val)) == right_val
                        log_case.set("success", result=result)
                        return result
                    result = python_type_to_bosh_type(type(left_val)) != right_val
                    log_case.set("success", result=result)
                    return result
                case "or":
                    result = bool(left_val) or bool(right_val)
                    log_case.set("success", result=result)
                    return result
                case "and":
                    result = bool(left_val) and bool(right_val)
                    log_case.set("success", result=result)
                    return result
                case "lt":
                    result = left_val < right_val
                    log_case.set("success", result=result)
                    return result
                case "gt":
                    result = self.left.execute(env) > self.right.execute(env)
                    log_case.set("success", result=result)
                    return result
                case "loet":
                    result = self.left.execute(env) <= self.right.execute(env)
                    log_case.set("success", result=result)
                    return result
                case "goet":
                    result = self.left.execute(env) >= self.right.execute(env)
                    log_case.set("success", result=result)
                    return result
                case _:
                    raise TraceError(node = self, cause = f"Unsupported operator '{self.operator}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)

    @logged(
        start=lambda self, v_table, f_table, inference_context, old_inference_value, new_inference_value: (
                f"Starting inference for binary operator '{self.operator}' with old inference value '{old_inference_value}' and new inference value '{new_inference_value}'..."
            ),
        success={
            "success": lambda self, v_table, f_table, inference_context, old_inference_value, new_inference_value: (
                f"Inference for binary operator '{self.operator}' completed successfully. Updated return type: '{self.child_return_types['self'][0]}'."
            )
        }
    )
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str],
                log_case: LogCase
                ) -> None:
        try:
            if "self" not in self.child_return_types:
                raise Exception(f"BinaryOp inference: No type information available for binary operator during inference. This node has not been checked. Node: {self}", self)
            if old_inference_value != self.child_return_types["self"][0]:
                raise Exception(f"BinaryOp inference: Old inference value '{old_inference_value}' does not match remembered return type '{self.child_return_types['self'][0]}' for binary operator. Something went wrong in the inference pathing. Node: {self}", self)
            if not t_h.is_compatible(new_inference_value, self.child_return_types["self"][0]):
                raise Exception(f"BinaryOp inference: New inference value '{new_inference_value}' is not compatible with remembered return type '{self.child_return_types['self'][0]}' for binary operator. Something went wrong in the inference pathing. Node: {self}", self)
            self.child_return_types["self"] = (new_inference_value.copy(), self)

            match self.operator:
                case "plus" | "minus" | "mult" | "div" | "pow" | "mod" :
                    
                    if t_h.is_only(new_inference_value, "date"):
                        if not self.operator in ["plus", "minus"]:
                            raise Exception(f"Binary operator '{self.operator}' cannot take 'date' and 'time' type. Only 'plus' and 'minus' can take 'date' and 'time'. ", self)
                        
                    

                    valid_input_types = set()
                    if t_h.contains(new_inference_value, "number"):
                        valid_input_types.add("number")

                    if t_h.contains(new_inference_value, "decimal"):
                        valid_input_types.add("decimal")
                    
                    if t_h.contains(new_inference_value, "date"):
                        valid_input_types.add("date")
                        valid_input_types.add("time") # because date can be returned from date +/- time.
                    
                    if t_h.contains(new_inference_value, "time"):
                        valid_input_types.add("time")
                        valid_input_types.add("date")
                        valid_input_types.add("number")
                        valid_input_types.add("decimal")

                    new_left_types = t_h.narrow(self.child_return_types["left"][0], valid_input_types)
                    new_right_types = t_h.narrow(self.child_return_types["right"][0], valid_input_types)

                    if not self.operator in ["plus", "minus"]:
                        if (t_h.is_only(new_left_types, "time") and t_h.is_only(new_right_types, "time")):
                            raise Exception(f"Binary operator '{self.operator}' cannot take 'time' and 'time' type. Only 'plus' and 'minus' can take 'time' and 'time'. ", self)
                        
                        if (t_h.is_only(new_left_types, "date") and t_h.is_only(new_right_types, "time")) or (t_h.is_only(new_left_types, "time") and t_h.is_only(new_right_types, "date")):
                            raise Exception(f"Binary operator '{self.operator}' cannot take 'date' and 'time' type. Only 'plus' and 'minus' can take 'date' and 'time'. ", self)
                    
                        if self.operator != "minus" and (t_h.is_only(new_left_types, "date") and t_h.is_only(new_right_types, "date")):
                            raise Exception(f"Binary operator '{self.operator}' cannot take 'date' and 'date' type. Only 'minus' can take 'date' and 'date'. ", self)
                    
                    if new_left_types != self.child_return_types["left"][0]:
                        self.left.inference(
                            v_table=v_table,
                            f_table=f_table,
                            inference_context=inference_context,
                            old_inference_value=self.child_return_types["left"][0].copy(),
                            new_inference_value=new_left_types.copy(),
                        )
                        self.child_return_types["left"] = (new_left_types.copy(), self.left)
                    if new_right_types != self.child_return_types["right"][0]:
                        self.right.inference(
                            v_table=v_table,
                            f_table=f_table,
                            inference_context=inference_context,
                            old_inference_value=self.child_return_types["right"][0].copy(),
                            new_inference_value=new_right_types.copy(),
                        )

                        self.child_return_types["right"] = (new_right_types.copy(), self.right)
                    
                    

                
                case "eq" | "neq" | "lt" | "gt" | "loet" | "goet":
                    raise Exception(
                        f"Inference for comparison operator '{self.operator}' is not supported because "
                        f"comparisons always return 'boolean'. If you are seeing this, something went "
                        f"wrong in inference pathing. new_inference_value: {new_inference_value}, "
                        f"old_inference_value: {old_inference_value}",
                        self
                    )
                
                case "eq_type" | "neq_type":
                    raise Exception(
                        f"Inference for type comparison operator '{self.operator}' is not supported because "
                        f"type comparisons always return 'boolean'. If you are seeing this, something went "
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
                
            log_case.set("success")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode
    def __post_init__(self):
        super().__init__()
    
    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking unary operation '{self.operator}' with operand '{self.operand}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Unary operation '{self.operator}' checked successfully with return type '{self.child_return_types['self'][0]}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            self.child_return_types.clear()
            operand_type = self.operand.check(
                v_table=v_table,
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
                            new_inference_value=narrowed.copy()
                        )

                    self.child_return_types["operand"] = (narrowed.copy(), self.operand)
                    self.child_return_types["self"] = (narrowed.copy(), self)
                    log_case.set("success")
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
                    log_case.set("success")
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
                    log_case.set("success")
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
                    log_case.set("success")
                    return narrowed
                
                case "sqrt":
                    valid_input_types = {"number", "decimal"}
                    if not t_h.is_compatible(operand_type, valid_input_types):
                        raise Exception(
                                        f"Unary operator 'sqrt' not supported for type '{operand_type}'. "
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
                        operand_type = narrowed.copy()

                    self.child_return_types["operand"] = (narrowed.copy(), self.operand)
                    self.child_return_types["self"] = ({"decimal"}, self)
                    log_case.set("success")
                    return {"decimal"}

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
                    log_case.set("success")
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
                    log_case.set("success")
                    return return_type
                
                case _:
                    raise Exception(f"Unsupported unary operator '{op}'", self)
        
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing unary operation '{self.operator}' with operand '{self.operand}'..."
        ),
        success={
            "success": lambda self, env, result: (
                f"Unary operation '{self.operator}' executed successfully. Result: {result}"
            )   
        }
    )
    def execute(self, env, log_case: LogCase) -> Any:
        try:
            match self.operator:
                case "neg":
                    result = -self.operand.execute(env)
                    log_case.set("success", result=result)
                    return result
                case "not":
                    result = not self.operand.execute(env)
                    log_case.set("success", result=result)
                    return result
                case "first":
                    result = self.operand.execute(env)[0]
                    log_case.set("success", result=result)
                    return result
                case "last":
                    result = self.operand.execute(env)[-1]
                    log_case.set("success", result=result)
                    return result
                case "floor":
                    result = math.floor(self.operand.execute(env))
                    log_case.set("success", result=result)
                    return result
                case "ceiling":
                    result = math.ceil(self.operand.execute(env))
                    log_case.set("success", result=result)
                    return result
                case "round":
                    result = int(round(self.operand.execute(env)))
                    log_case.set("success", result=result)
                    return result
                case "sqrt":
                    result = math.sqrt(self.operand.execute(env))
                    log_case.set("success", result=result)
                    return result
                case _:
                    raise TraceError(node = self, cause = f"Unsupported unary operator '{self.operator}'")
                
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    
    @logged(
        start=lambda self, v_table, f_table, inference_context, old_inference_value, new_inference_value: (
            f"Starting inference for unary operator '{self.operator}' with old inference value '{old_inference_value}' and new inference value '{new_inference_value}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, old_inference_value, new_inference_value: (
                f"Inference for unary operator '{self.operator}' completed successfully. Updated return type: '{self.child_return_types['self'][0]}'."
            )
        }
    )
    def inference(self,
                    v_table: ScopeStack,
                    f_table: FuncTable,
                    inference_context: InferenceContext,
                    old_inference_value: set[str],
                    new_inference_value: set[str],
                    log_case: LogCase
                ) -> None:
        
        try:
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
                    log_case.set("success")
                    return

                case "sqrt":
                    raise Exception(f"Inference for 'sqrt' operator is not supported because it only supports 'number' and 'decimal' types and returns 'decimal', so there is no need for inference. "
                                    f"If you are seeing this error, it means something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)
                    

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
                    log_case.set("success")
                    return

                case _:
                    raise Exception(f"Inference for unary operator '{self.operator}' is not supported. If you are seeing this error, it means something went wrong somewhere. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}", self)

        except Exception as e:
            raise TraceError(node = self, cause = e)
@dataclass
class AccessOp(ASTNode):
    target: Optional[ASTNode]
    operation: str
    argument: Optional[ASTNode] = None
    def __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking access operation '{self.operation}' with target '{self.target}' and argument '{self.argument}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Access operation '{self.operation}' checked successfully with return type '{self.child_return_types['self'][0]}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
        try:
            self.child_return_types.clear()

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
                    log_case.set("success")
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
                    log_case.set("success")
                    return {"time"}
                
                case "first" | "last":
                    if target_type is None:
                        raise Exception(f"Access operation '{op}' requires a target, but no target was provided.")
                    if not t_h.has_list_type(target_type):
                        raise Exception(f"Cannot get '{op}' element of type '{target_type}'. {op} Expected a list.")
                    
                    if t_h.has_non_list_type(target_type):
                        new_target_type = t_h.get_all_list_types(target_type)
                        self.target.inference(
                            v_table=v_table,
                            f_table=f_table,
                            inference_context=inference_context,
                            old_inference_value=target_type.copy(),
                            new_inference_value=new_target_type.copy(),
                        )

                        target_type = new_target_type.copy()

                    self.child_return_types["target"] = (target_type.copy(), self.target)
                    return_type = t_h.get_list_element_types(target_type)
                    self.child_return_types["self"] = (return_type.copy(), self)
                    log_case.set("success")
                    return return_type

                case "length":
                    if target_type is None:
                        raise Exception(f"Access operation '{op}' requires a target, but no target was provided.")
                    if not t_h.has_list_type(target_type):
                        if not t_h.contains(target_type, "text"):
                            raise Exception(f"Cannot get length of type '{target_type}'. {op} Expected a list.")
                    if not t_h.is_only(target_type, "text"):
                        if t_h.has_non_list_type(target_type):

                            new_target_type = t_h.get_all_list_types(target_type)
                            if t_h.contains(target_type, "text"):
                                new_target_type.add("text")
                            self.target.inference(
                                v_table=v_table,
                                f_table=f_table,
                                inference_context=inference_context,
                                old_inference_value=target_type.copy(),
                                new_inference_value=new_target_type.copy(),
                            )

                            target_type = new_target_type.copy()
                    
                    self.child_return_types["target"] = (target_type.copy(), self.target)
                    self.child_return_types["self"] = ({"number"}, self)
                    log_case.set("success")
                    return {"number"}
                    

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
                    log_case.set("success")
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
                    log_case.set("success")
                    return return_types
                
                case "now":
                    self.child_return_types["self"] = ({"date"}, self)
                    log_case.set("success")
                    return {"date"}

                case "here":
                    self.child_return_types["self"] = ({"text"}, self)
                    log_case.set("success")
                    return {"text"}
                
                case _:
                    raise Exception(f"Unsupported access operation '{op}'", self)
            
        except Exception as e:
            raise TraceError(node = self, cause = e)
    

    @logged(
        start=lambda self, env: (
            f"Executing access operation '{self.operation}' with target '{self.target}' and argument '{self.argument}'..."
        ),
        success={
            "success": lambda self, env, result: (
                f"Access operation '{self.operation}' executed successfully. Result: {result}"
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> Any:
        try:
            target_value = self.target.execute(env) if self.target else None
            arg_value = self.argument.execute(env) if self.argument else None
            match self.operation:
                case "file_name":
                    result = os.path.basename(target_value)
                    log_case.set("success", result=result)
                    return result
                case "age":
                    time = os.path.getmtime(target_value)
                    file_date = datetime.datetime.fromtimestamp(time)
                    now = datetime.datetime.now()
                    log_case.set("success", result=result)
                    return int((now - file_date).total_seconds() * 1000)
                case "starts_with":
                    result = target_value.startswith(arg_value)
                    log_case.set("success", result=result)
                    return result
                case "ends_with":
                    result = target_value.endswith(arg_value)
                    log_case.set("success", result=result)
                    return result
                case "regex":
                    result = re.search(arg_value, target_value) is not None
                    log_case.set("success", result=result)
                    return result
                case "length":
                    result = len(target_value)
                    log_case.set("success", result=result)
                    return result
                case "first":
                    result = target_value[0]
                    log_case.set("success", result=result)

                    return result
                case "last":
                    result = target_value[-1]
                    log_case.set("success", result=result)
                    return result
                case "unit":
                    # This will be handled by the Unit AST node, so we can just return the value here
                    log_case.set("success", result=target_value)
                    return target_value
                case "now":
                    result = datetime.datetime.now()
                    log_case.set("success", result=result)
                    return result
                case "here":
                    result = env.get_current_directory()
                    log_case.set("success", result=result)
                    return result
                case _:
                    raise TraceError(node = self, cause = f"Unsupported access operation '{self.operation}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    @logged(
        start=lambda self, v_table, f_table, inference_context, old_inference_value, new_inference_value: (
                f"Starting inference for access operation '{self.operation}' with old inference value '{old_inference_value}' and new inference value '{new_inference_value}'..."
            ),
        success={
            "success": lambda self, v_table, f_table, inference_context, old_inference_value, new_inference_value: (
                f"Inference for access operation '{self.operation}' completed successfully. Updated return type: '{self.child_return_types['self'][0]}'."
            )
        }
    )
    def inference(self, v_table, f_table, inference_context, old_inference_value, new_inference_value, log_case: LogCase) -> None:
        try:
            if "self" not in self.child_return_types:
                raise Exception(f"AccessOp inference: No type information available for access operation during inference. This node has not been checked. Node: {self}", self)
            if len(self.child_return_types["self"][0]) == 1:
                raise Exception(f"AccessOp inference: Only one possible return type '{self.child_return_types['self'][0]}' for access operation '{self.operation}'. Inference should not be necessary. Node: {self}", self)
            if old_inference_value != self.child_return_types["self"][0]:
                raise Exception(f"AccessOp inference: Old inference value '{old_inference_value}' does not match remembered return types '{self.child_return_types['self'][0]}' for access operation '{self.operation}'. "
                                f"Something went wrong in the inference pathing. Node: {self}", self)
            match self.operation:

                case "file_name" | "age" | "starts_with" | "ends_with" | "regex" | "length" | "now" | "here":
                    raise Exception(
                        f"Inference for access operation '{self.operation}' is not supported because it only supports one return type, so there is no need for inference. If you are seeing this error, "
                        f"it means something went wrong in the inference pathing. new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}",
                        self
                    )

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

                case "first" | "last":
                    if "target" not in self.child_return_types:
                        raise Exception(f"AccessOp inference: No type information available for target during inference of access operation '{self.operation}'. This node has not been checked. Node: {self}", self)
                    remembered_target_types = self.child_return_types["target"][0]

                    new_target_value = t_h.make_set_list_types(new_inference_value)
                    if new_target_inference != remembered_target_types:
                        self.target.inference(
                            v_table=v_table,
                            f_table=f_table,
                            inference_context=inference_context,
                            old_inference_value=remembered_target_types.copy(),
                            new_inference_value=new_target_value.copy(),
                        )
                        self.child_return_types["target"] = (new_target_value.copy(), self.target)
                    
                    
                    
                case _:
                    raise Exception(
                        f"Inference for access operation '{self.operation}' is not supported. If you are seeing this error, it means something went wrong somewhere. "
                        f"new_inference_value: {new_inference_value}, old_inference_value: {old_inference_value}",
                        self)
            
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)

@dataclass
class Random(ASTNode):
    from_: ASTNode
    to: ASTNode

    def __post_init__(self):
        super().__init__()

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Starting type check for random operator with 'from' operand '{self.from_}' and 'to' operand '{self.to}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Type check for random operator passed successfully. Determined return type: {self.child_return_types['self'][0]}"
            )
        }
    )
    def check(self, v_table, f_table, inference_context, log_case: LogCase) -> set[str]:
        try:
            if self.from_ is None or self.to is None:
                raise Exception(f"Random operator requires both 'from' and 'to' operands, but one or both were not provided.")

            from_type = self.from_.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            
            if from_type is None:
                raise Exception(f"Could not determine type of 'from' operand in random operator.")

            if not t_h.contains(from_type, "number"):
                raise Exception(f"Random operator 'from' operand must contain 'number', got '{from_type}'.")
            
            if from_type != {"number"}:
                self.from_.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=from_type.copy(),
                    new_inference_value={"number"},
                )
                from_type = {"number"}

            to_type = self.to.check(v_table=v_table, f_table=f_table, inference_context=inference_context)

            if to_type is None:
                raise Exception(f"Could not determine type of 'to' operand in random operator.")
            
            if not t_h.contains(to_type, "number"):
                raise Exception(f"Random operator 'to' operand must contain 'number', got '{to_type}'.")
            
            if to_type != {"number"}:
                self.to.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=to_type.copy(),
                    new_inference_value={"number"},
                )
                to_type = {"number"}

            self.child_return_types["from"] = (from_type.copy(), self.from_)
            self.child_return_types["to"] = (to_type.copy(), self.to)
            self.child_return_types["self"] = ({"number"}, self)

            log_case.set("success")

            return {"number"}

        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env):
        import random
        try:
            from_value = self.from_.execute(env)
            to_value = self.to.execute(env)
            return random.randint(from_value, to_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)

          