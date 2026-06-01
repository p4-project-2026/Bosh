from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedInput, UnexpectedToken, UnexpectedCharacters

from bosh.helper_functions.paths import PathsHelper
from ..abstract_syntax import *

RED = "\033[31m"
CYAN = "\033[36m"
RESET_ALL = "\033[0m"

def parseBosh(processed_code):
    with open(PathsHelper().get_src_path().joinpath("bosh/interpreter/lexparser/bosh_lang.lark"), "r", encoding="utf-8") as f:
        grammar = f.read()

    parser = Lark(grammar, start="program", parser="lalr", propagate_positions=True)

    try:
        tree = parser.parse(processed_code)
    except (UnexpectedInput, UnexpectedToken, UnexpectedCharacters) as e:
        context = e.get_context(processed_code)
        message = f"{RED}Syntax error: {str(e)}{RESET_ALL}"
        if context:
            message += f"Context:\n{CYAN}{context}{RESET_ALL}"
        raise SyntaxError(message.strip()) from e

    return tree

def createAST(tree, filename: str = None) -> Program:
    return BoshTransformer(filename=filename).transform(tree)

@v_args(meta=True)
class BoshTransformer(Transformer):
    def __init__(self, filename: str = None):
        self._filename = filename

    def program(self, meta, args):
        node = Program(block=args[0])
        node.set_meta(meta, self._filename)
        return node

    def block(self, meta, args):
        node = Block(statements=args)
        node.set_meta(meta, self._filename)
        return node

    # GENERAL STATEMENTS ----------------------------------------
    def if_unable(self, meta, args):
        node = Fallback(primary_stmt=args[0], fallback_stmt=args[1])
        node.set_meta(meta, self._filename)
        return node

    def if_else(self, meta, args):
        node = IfElse(
            condition=args[0],
            then_branch=args[1],
            else_branch=args[2] if len(args) > 2 else None,
        )
        node.set_meta(meta, self._filename)
        return node

    def for_all(self, meta, args):
        node = ForAll(iterator_name=str(args[0]), iterable=args[1], body=args[2])
        node.set_meta(meta, self._filename)
        return node

    def repeat(self, meta, args):
        node = RepeatUntil(condition=args[0], body=args[1])
        node.set_meta(meta, self._filename)
        return node
    
    def count(self, meta, args):
        iterator_name = str(args[0]) if isinstance(args[0], str) else None
        args = args[1:] if iterator_name else args
        from_ = args[0]
        to_ = args[1]
        body = args[2]
        node = Count(iterator_name=iterator_name, from_=from_, to_=to_, body=body)
        node.set_meta(meta, self._filename)
        return node

    def quit(self, meta, args):
        node = Quit()
        node.set_meta(meta, self._filename)
        return node

    def print(self, meta, args):
        node = Print(expression=args[0])
        node.set_meta(meta, self._filename)
        return node

    def return_(self, meta, args):
        value = args[0] if args else NullLiteral()
        node = Return(expression=value)
        node.set_meta(meta, self._filename)
        return node

    def continue_(self, meta, args):
        node = Continue()
        node.set_meta(meta, self._filename)
        return node

    def break_(self, meta, args):
        node = Break()
        node.set_meta(meta, self._filename)
        return node

    def assign_to_list(self, meta, args):
        node = ListAssign(target=args[0], index=args[1], value=args[2])
        node.set_meta(meta, self._filename)
        return node

    def add_to_list(self, meta, args):
        index = args[3] if len(args) > 3 else None
        node = ListAdd(op=args[0], item=args[1], target=args[2], index=index)
        node.set_meta(meta, self._filename)
        return node

    def remove_from_list(self, meta, args):
        node = ListRemove(target=args[1], item=args[0])
        node.set_meta(meta, self._filename)
        return node
    
    def remove_from_list_at(self, meta, args):
        node = ListRemoveAt(target=args[1], index=args[0])
        node.set_meta(meta, self._filename)
        return node

    def call_func(self, meta, args):
        name = str(args[0])
        arguments = args[1:] if len(args) > 1 else []
        node = TaskCall(name=name, arguments=arguments)
        node.set_meta(meta, self._filename)
        return node

    # DEFINITIONS ----------------------------------------
    def assign(self, meta, args):
        target_node = Identifier(name=str(args[0]))
        node = Assign(target=target_node, value=args[1])
        node.set_meta(meta, self._filename)
        return node

    def assign_type(self, meta, args):
        target_node = Identifier(name=str(args[0]))
        var_type = args[1]
        value = args[2] if len(args) > 2 else None
        
        if var_type == "list" and value is None:
            var_type = "list<any>"
            value = ListLiteral(elements=[])

        node = AssignType(target=target_node, var_type=var_type, value=value)
        node.set_meta(meta, self._filename)
        return node

    def assign_func(self, meta, args):
        parameters = [str(param) for param in args[1:-1]]
        body = args[-1]
        node = TaskDecl(name=str(args[0]), parameters=parameters, body=body)
        node.set_meta(meta, self._filename)
        return node
    
    # DOMAIN-SPECIFIC STATEMENTS ----------------------------------------
    def go_to(self, meta, args):
        node = GoTo(path=args[0])
        node.set_meta(meta, self._filename)
        return node
    
    def go_up(self, meta, args):
        node = GoUp()
        node.set_meta(meta, self._filename)
        return node

    def make(self, meta, args):
        new = False
        if args[0] == "new":
            new = True
            args = args[1:]
        location = args[2] if len(args) > 2 else None
        node = Make(new=new, entity_type=args[0], name=args[1], location=location)
        node.set_meta(meta, self._filename)
        return node

    def rename(self, meta, args):
        node = Rename(target=args[0], new_name=args[1])
        node.set_meta(meta, self._filename)
        return node

    def delete(self, meta, args):
        node = Delete(target=args[0])
        node.set_meta(meta, self._filename)
        return node

    def copy_from_to(self, meta, args):
        node = Copy(source=args[0], target=args[1])
        node.set_meta(meta, self._filename)
        return node

    def move(self, meta, args):
        node = Move(source=args[0], target=args[1])
        node.set_meta(meta, self._filename)
        return node

    def read(self, meta, args):
        node = Read(source=args[0])
        node.set_meta(meta, self._filename)
        return node

    def write(self, meta, args):
        node = Write(target=args[1], data=args[0])
        node.set_meta(meta, self._filename)
        return node

    def execute(self, meta, args):
        node = Execute(target=args[0] if args else None)
        node.set_meta(meta, self._filename)
        return node

    def pause(self, meta, args):
        node = Pause()
        node.set_meta(meta, self._filename)
        return node

    def wait(self, meta, args):
        node = Wait(time=args[0] if args else None)
        node.set_meta(meta, self._filename)
        return node

    def input(self, meta, args):
        node = Input(prompt=args[0] if args else None)
        node.set_meta(meta, self._filename)
        return node

    # EXPRESSIONS ----------------------------------------
    def call_func(self, meta, args):
        return self.func(meta, args)

    def or_(self, meta, args):
        node = BinaryOp(operator="or", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def and_(self, meta, args):
        node = BinaryOp(operator="and", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def eq(self, meta, args):
        node = BinaryOp(operator="eq", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def neq(self, meta, args):
        node = BinaryOp(operator="neq", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node
    
    def eq_type(self, meta, args):
        node = BinaryOp(operator="eq_type", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node
    
    def neq_type(self, meta, args):
        node = BinaryOp(operator="neq_type", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def gt(self, meta, args):
        node = BinaryOp(operator="gt", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def lt(self, meta, args):
        node = BinaryOp(operator="lt", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def goet(self, meta, args):
        node = BinaryOp(operator="goet", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def loet(self, meta, args):
        node = BinaryOp(operator="loet", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def plus(self, meta, args):
        node = BinaryOp(operator="plus", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def minus(self, meta, args):
        node = BinaryOp(operator="minus", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def mult(self, meta, args):
        node = BinaryOp(operator="mult", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def div(self, meta, args):
        node = BinaryOp(operator="div", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def mod(self, meta, args):
        node = BinaryOp(operator="mod", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node
    
    def pow(self, meta, args):
        node = BinaryOp(operator="pow", left=args[0], right=args[1])
        node.set_meta(meta, self._filename)
        return node

    def sqrt(self, meta, args):
        node = UnaryOp(operator="sqrt", operand=args[0])
        node.set_meta(meta, self._filename)
        return node

    def not_(self, meta, args):
        node = UnaryOp(operator="not", operand=args[0])
        node.set_meta(meta, self._filename)
        return node

    def neg(self, meta, args):
        node = UnaryOp(operator="neg", operand=args[0])
        node.set_meta(meta, self._filename)
        return node

    def floor(self, meta, args):
        node = UnaryOp(operator="floor", operand=args[0])
        node.set_meta(meta, self._filename)
        return node

    def ceiling(self, meta, args):
        node = UnaryOp(operator="ceiling", operand=args[0])
        node.set_meta(meta, self._filename)
        return node

    def round(self, meta, args):
        node = UnaryOp(operator="round", operand=args[0])
        node.set_meta(meta, self._filename)
        return node

    def list_look(self, meta, args):
        node = ListLookup(target=args[0], index=args[1])
        node.set_meta(meta, self._filename)
        return node
    
    def text_look(self, meta, args):
        node = TextLookup(target=args[1], index=args[0])
        node.set_meta(meta, self._filename)
        return node
    
    def length(self, meta, args):
        node = AccessOp(target=args[0], operation="length")
        node.set_meta(meta, self._filename)
        return node

    def first(self, meta, args):
        node = AccessOp(target=args[0], operation="first")
        node.set_meta(meta, self._filename)
        return node

    def last(self, meta, args):
        node = AccessOp(target=args[0], operation="last")
        node.set_meta(meta, self._filename)
        return node

    def regex(self, meta, args):
        node = AccessOp(target=args[0], operation="regex", argument=args[1])
        node.set_meta(meta, self._filename)
        return node

    def age(self, meta, args):
        node = AccessOp(target=args[0], operation="age")
        node.set_meta(meta, self._filename)
        return node

    def file_name(self, meta, args):
        node = AccessOp(target=args[0], operation="file_name")
        node.set_meta(meta, self._filename)
        return node

    def starts_with(self, meta, args):
        node = AccessOp(target=args[0], operation="starts_with", argument=args[1])
        node.set_meta(meta, self._filename)
        return node

    def ends_with(self, meta, args):
        node = AccessOp(target=args[0], operation="ends_with", argument=args[1])
        node.set_meta(meta, self._filename)
        return node
    
    def contains(self, meta, args):
        node = AccessOp(target=args[0], operation="contains", argument=args[1])
        node.set_meta(meta, self._filename)
        return node

    def unit(self, meta, args):
        node = Unit(value=args[0], unit_type=str(args[1]).lower())
        node.set_meta(meta, self._filename)
        return node
    
    def type_cast(self, meta, args):
        node = TypeCast(target=args[0], target_type=(args[1]))
        node.set_meta(meta, self._filename)
        return node

    # LITERALS AND IDENTIFIERS ----------------------------------------
    def var(self, meta, args):
        node = Identifier(name=str(args[0]))
        node.set_meta(meta, self._filename)
        return node

    def func(self, meta, args):
        name = str(args[0])
        arguments = args[1:] if len(args) > 1 else []
        node = TaskCall(name=name, arguments=arguments)
        node.set_meta(meta, self._filename)
        return node

    def number(self, meta, args):
        node = NumberLiteral(value=int(args[0]))
        node.set_meta(meta, self._filename)
        return node
        
    def decimal(self, meta, args):
        node = DecimalLiteral(value=float(args[0]))
        node.set_meta(meta, self._filename)
        return node

    def text(self, meta, args):
        if len(args) == 1 and isinstance(args[0], StringLiteral):
            node = args[0]
            node.set_meta(meta, self._filename)
            return node

        parts = []
        for part in args:
            parts.append(part)

        node = InterpolatedString(parts=parts)
        node.set_meta(meta, self._filename)
        return node
    
    def date(self, meta, args):
        node = DateLiteral(value=str(args[0]))
        node.set_meta(meta, self._filename)
        return node
    
    def str_chars(self, meta, args):
        content = "".join(str(arg) for arg in args)
        content = content.replace(r'\"', '"').replace(r'\{', '{').replace(r'\}', '}').replace(r'\\', '\\')
        node = StringLiteral(value=content)
        node.set_meta(meta, self._filename)
        return node
    
    def interp(self, meta, args):
        return args[0]

    def boolean(self, meta, args):
        value = bool(str(args[0]).lower() == "true")
        node = BooleanLiteral(value=value)
        node.set_meta(meta, self._filename)
        return node

    def null(self, meta, args):
        node = NullLiteral()
        node.set_meta(meta, self._filename)
        return node

    def path(self, meta, args):
        full_path = "/".join([arg.value for arg in args])
        node = StringLiteral(value=full_path)
        node.set_meta(meta, self._filename)
        return node

    def list(self, meta, args):
        node = ListLiteral(elements=args)
        node.set_meta(meta, self._filename)
        return node

    def now(self, meta, args):
        node = AccessOp(target=None, operation="now", argument=args[0] if args else None)
        node.set_meta(meta, self._filename)
        return node

    def here(self, meta, args):
        node = AccessOp(target=None, operation="here")
        node.set_meta(meta, self._filename)
        return node

    def random(self, meta, args):
        node = Random(from_=args[0], to=args[1])
        node.set_meta(meta, self._filename)
        return node

    def paren(self, meta, args):
        return args[0]

    def second(self, meta, args):
        return "second"

    def minute(self, meta, args):
        return "minute"

    def hour(self, meta, args):
        return "hour"

    def day(self, meta, args):
        return "day"

    def month(self, meta, args):
        return "month"

    def year(self, meta, args):
        return "year"
    
    def TYPE(self, token):
        type_str = str(token.value).lower()
        match(type_str):
            case "int":
                type_str = "number"
            case "float":
                type_str = "decimal"
            case "string":
                type_str = "text"
            case "bool":
                type_str = "boolean"
            case "list":
                type_str = "list<any>"
        node = Type(name=type_str)
        node.set_meta(None, self._filename)
        return node
    
    def PATH(self, token):
        full_path = str(token.value)
        node = Type(name=full_path)
        node.set_meta(None, self._filename)
        return node
    
    def DT(self, token):
        type_str = str(token.value).lower()
        node = Type(name = type_str)
        node.set_meta(None, self._filename)
        return node
    
    def list_files(self, meta, args):
        node = Lookdir(location=args[0])
        node.set_meta(meta, self._filename)
        return node
    
    def text_slice(self, meta, args):
        node = TextSlice(text=args[0], from_index=args[1], to_index=args[2])
        node.set_meta(meta, self._filename)
        return node
    
    def textcutter(self, meta, args):
        node = Textcutter(text=args[0], cut_from=args[1], index=args[2])
        node.set_meta(meta, self._filename)
        return node
    
    def text_split(self, meta, args):
        node = TextSplit(text=args[0], delimiter=args[1])
        node.set_meta(meta, self._filename)
        return node