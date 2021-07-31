from ..resources.tokens.token_types import TokenType
from ..resources.symbol_table.symbol_table import SymbolTable
from ..resources.nodes.nodes import *
from typing import Union, Optional
from itertools import zip_longest


class Interpreter:
    """
    Class for the interpreter of the language.

    The interpreter will read the abstract syntax tree and nodes and turn it into a specific value.
    """

    def __init__(self) -> None:
        self.symbol_table = SymbolTable()
        self.symbol_table["true"] = Number(1)
        self.symbol_table["false"] = Number(0)
        self.symbol_table["null"] = Number(0)

    def visit(self, node: Union[NumberNode, BinOpNode, StringNode, UnaryOpNode,
                                VarAssignNode, VarAccessNode], symbol_table: Optional[SymbolTable] = None,
              superclass: Optional[bool] = False) -> Union[
        Number, String]:
        """Visits node inputted with the functions below."""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        if symbol_table is None:
            symbol_table = self.symbol_table
        if method_name == 'visit_FunctionCallNode':
            return method(node, symbol_table, superclass)
        else:
            return method(node, symbol_table)

    def no_visit_method(self, node: None, symbol_table: SymbolTable):
        """Raised when the visit method is not specified for a certain node."""
        raise Exception(f'No visit_{type(node).__name__} method defined.')

    def visit_FunctionNode(self, node: FunctionNode, symbol_table: SymbolTable) -> None:
        """
        Defines function in the global symbol table,
        stored for reference till function call.
        """
        symbol_table[node.func_name] = node

    def visit_AccessNode(self, node: AccessNode, symbol_table: SymbolTable):
        """Function used to access an item within the item to access."""
        if node.accessor.name == "super":
            accessing = self.visit(node.accessor, symbol_table["inst"])
        else:
            accessing = self.visit(node.accessor, symbol_table)
        if isinstance(accessing, tuple):
            local_symbol_table = accessing[0].local_symbol_table["inst"]
            try:
                item = self.visit(node.item_to_access, local_symbol_table)
            except KeyError:
                try:
                    item = self.visit(node.item_to_access, symbol_table)
                except KeyError:
                    item = self.visit(node.item_to_access, accessing[1])
        elif isinstance(node.item_to_access, FunctionCallNode):
            result = accessing[node.item_to_access.func_name]
            result = FunctionCallNode(result.func_name, node.item_to_access.params)
            if node.accessor.name == 'super':
                item = self.visit(result, symbol_table["inst"], True)
            else:
                item = self.visit(result, accessing)
        elif isinstance(node.item_to_access, NumberNode):
            try:
                item = self.visit(node.item_to_access, symbol_table)
                if isinstance(accessing, String):
                    item = String(accessing.vals[item.value])
                else:
                    item = Number(accessing.vals[item.value])
            except KeyError:
                return f'{node.item_to_access.value} is not an index'
        else:
            try:
                item = self.visit(node.item_to_access, accessing)
            except KeyError:
                item = self.visit(node.item_to_access, symbol_table)

        return item

    def visit_ObjectNode(self, node: ObjectNode, symbol_table: SymbolTable) -> None:
        """Interprets an object and will create the object."""
        symbol_table[node.name] = (node, {})
        for class_attr in node.class_attrs:
            symbol_table[node.name][1][class_attr.name] = self.visit(class_attr.value, symbol_table)
        for func in [val for val in node.methods.values()]:
            self.visit(func, node.local_symbol_table)

        for func_spec in [val_spec for val_spec in node.special_methods.values()]:
            self.visit(func_spec, node.local_symbol_table)

    def visit_ReturnNode(self, node: ReturnNode, symbol_table: SymbolTable) -> Union[Number, String]:
        """Used for when using the return keyword."""
        result = self.visit(node.expression, symbol_table)
        return result

    def visit_ExecuteBuiltInsNode(self, node: ExecuteBuiltInsNode, symbol_table: SymbolTable) -> Union[tuple,
                                                                                                       String, Number]:
        """Executes built-in functions."""
        node.params = [self.visit(param, symbol_table) for param in node.params]
        if node.name == "print":
            return ('print', '\n'.join([str(print_param.value) for print_param in node.params]))
        elif node.name == "pop":
            lst = node.params[0]
            idx = node.params[1].value
            del_end = idx != (to_del := len(lst.vals.keys()) - 1)
            del lst.vals[idx]
            for key, val in zip(list(lst.vals.keys())[idx:],
                                list(lst.vals.values())[idx:]):
                lst.vals[key - 1] = val
            if del_end:
                del lst.vals[to_del]

            lst.value = [lst.vals[index].value for index, _ in enumerate(lst.vals.values())]

            return lst
        elif node.name == 'append':
            lst = node.params[0]
            item = node.params[1]
            lst.vals[sorted(list(lst.vals.keys()))[-1] + 1] = item
            lst.value = [lst.vals[idx].value for idx, _ in enumerate(lst.vals.values())]
            return lst

        elif node.name == 'extend':
            lst = node.params[0]
            second_lst = node.params[1]
            cur_idx = sorted(list(lst.vals.keys()))[-1]
            for val in second_lst.vals.values():
                cur_idx += 1
                lst.vals[cur_idx] = val

            lst.value = [lst.vals[idx].value for idx, _ in enumerate(lst.vals.values())]
            return lst
        else:
            return node.fetch_func()

    def visit_FunctionCallNode(self, node: FunctionCallNode, symbol_table: SymbolTable,
                               superclass: bool = False) -> None:
        """Executes function called with said parameters"""
        if symbol_table:
            if superclass:
                res = symbol_table['super'][node.func_name]
            else:
                res = symbol_table[node.func_name]
            if isinstance(res, tuple):
                class_node = symbol_table[node.func_name][0]

                new_symbol_table = SymbolTable()
                new_symbol_table["inst"] = SymbolTable()
                inst = new_symbol_table["inst"]
                initialization = symbol_table[node.func_name][0].special_methods['init']
                node.params = [self.visit(param, symbol_table) for param in node.params]
                inst["params"] = {}
                for param, name_of_param in zip(node.params, initialization.params[1:]):
                    inst["params"][name_of_param.value] = param

                if class_node.inherit:
                    inheriting_class = symbol_table[class_node.inherit][0]
                    super_cls = {'super': {}}
                    for key_spec, super_spec in zip_longest(class_node.special_methods.keys(),
                                                            inheriting_class.special_methods.keys()):
                        inst[key_spec] = class_node.special_methods.get(key_spec)
                        if super_spec:
                            super_cls['super'][super_spec] = inheriting_class.special_methods.get(super_spec)
                    for key, key_super in zip_longest(class_node.methods.keys(),
                                                      inheriting_class.methods.keys()):
                        inst[key] = class_node.methods.get(key)
                        if key_super:
                            super_cls['super'][key_super] = inheriting_class.methods.get(key_super)
                    inst.symbols.update(super_cls)
                else:
                    inst.symbols.update(class_node.methods)

                new_obj = ObjectNode(name=class_node.name, methods=class_node.methods,
                                     special_methods=class_node.special_methods,
                                     attributes=class_node.attributes, symbol_table=new_symbol_table,
                                     global_attrs=class_node.class_attrs)
                new_item = (new_obj, new_obj.class_attrs)

                for line in initialization.body:
                    if line:
                        self.visit(line, new_obj.local_symbol_table)

                if "params" in inst.symbols.keys():
                    del inst["params"]
                return new_item

            else:
                node.params = [self.visit(param, symbol_table) for param in node.params]
                if 'inst' in [param.value for param in (
                symbol_table['super'][node.func_name] if superclass else symbol_table[node.func_name]).params]:
                    node.params = [symbol_table] + node.params
                try:
                    if superclass:
                        func = symbol_table['super'][node.func_name]
                    else:
                        func = symbol_table[node.func_name]
                except KeyError:
                    func = self.symbol_table[node.func_name]

                if 'inst' in func.local_symbol_table.symbols.keys() and not isinstance(func.local_symbol_table["inst"],
                                                                                       SymbolTable):
                    func.local_symbol_table["inst"] = symbol_table
                    func.local_symbol_table["inst"]["params"] = {}
                for param, name_of_param in zip(node.params, func.params):
                    if 'inst' in func.local_symbol_table.symbols.keys():
                        func.local_symbol_table["inst"]["params"][name_of_param.value] = param
                        if name_of_param.value in func.local_symbol_table.symbols.keys() and name_of_param.value != 'inst':
                            del func.local_symbol_table[name_of_param.value]
                    else:
                        func.local_symbol_table[name_of_param.value] = param
                for line in func.body:
                    if line:
                        try:
                            result = self.visit(line, func.local_symbol_table)
                        except KeyError:
                            result = self.visit(line, symbol_table)
                        if isinstance(line, ReturnNode):
                            res = result
                            if isinstance(line.expression, AccessNode) and \
                                    isinstance(line.expression.item_to_access, FunctionCallNode):
                                if 'inst' in func.local_symbol_table.symbols.keys():
                                    del func.local_symbol_table["inst"]["params"]
                            return res
                        elif isinstance(result, ReturnNode):
                            res = self.visit(result, func.local_symbol_table)
                            if 'inst' in func.local_symbol_table.symbols.keys():
                                del func.local_symbol_table["inst"]["params"]
                            return res
                if 'inst' in func.local_symbol_table.symbols.keys():
                    del func.local_symbol_table["inst"]["params"]

    def visit_WhileNode(self, node: WhileNode, symbol_table: SymbolTable) -> None:
        """
        Executes code within while loop.

        WhileNode is a class interpreted by this function which will be checking a condition and run
        code within the block while under that certain condition.
        """
        while True:
            if self.visit(node.cond, symbol_table).value == 0:
                break
            else:
                for expr in node.body:
                    if expr is not None:
                        if isinstance(expr, ReturnNode):
                            return expr
                        res = self.visit(expr, symbol_table)
                        if isinstance(res, ReturnNode):
                            return res

    def visit_ForNode(self, node: ForNode, symbol_table: SymbolTable) -> Union[None, ReturnNode]:
        """
        Executes code within the for loop.

        ForNode is a class interpreted by this function which sets forth the guidelines
        for said for loop.
        """
        # initializing node_var
        symbol_table[node.var_name.name] = self.visit(node.var_name.value, symbol_table)
        end_value = self.visit(node.end_value, symbol_table)
        body = node.body
        step_value = self.visit(node.step_value, symbol_table)
        check = self.visit(node.start_value, symbol_table)
        if step_value.value > 0:
            condition = lambda: bool((check < end_value).value)
        else:
            condition = lambda: bool((check > end_value).value)

        while condition() is True:
            for expr in body:
                if expr is not None:
                    if isinstance(expr, ReturnNode):
                        return expr
                    res = self.visit(expr, symbol_table)
                    if isinstance(res, ReturnNode):
                        return res
            symbol_table[node.var_name.name] += Number(step_value)
            check = check + step_value

    def visit_NumberNode(self, node: NumberNode, symbol_table: SymbolTable) -> String:
        """
        Returns a Number class from NumberNode

        NumberNode is a class for an integer or float type in this language.
        """
        return Number(node.tok.value)

    def visit_ListNode(self, node: ListNode, symbol_table: SymbolTable) -> List:
        """
        Returns List class from ListNode

        The List class is a class for the list datatype in the language.
        """
        node.list = {idx: self.visit(ele, symbol_table) for idx, ele in
                     enumerate(node.list.values())}
        return List(node.list)

    def visit_StringNode(self, node: StringNode, symbol_table: SymbolTable) -> String:
        """
        Returns a String class from StringNode

        StringNode is a class for the string type in this language.
        """
        return String(node.tok.value)

    def visit_BinOpNode(self, node: BinOpNode, symbol_table: SymbolTable) -> Union[Number, String]:
        """
        Returns a Number or String class depending on the binary operation being done

        Shortens binary operation to a single result
        """
        left_node = self.visit(node.left_node, symbol_table)
        right_node = self.visit(node.right_node, symbol_table)
        if type(left_node).__name__ == 'Number' and \
                type(right_node).__name__ == 'Number':
            if node.op_tok.token_type == TokenType.PLUS:
                return Number(left_node) + Number(right_node)
            elif node.op_tok.token_type == TokenType.MINUS:
                return Number(left_node) - Number(right_node)
            elif node.op_tok.token_type == TokenType.MULT:
                return Number(left_node) * Number(right_node)
            elif node.op_tok.token_type == TokenType.DIV:
                return Number(left_node) / Number(right_node)
            elif node.op_tok.token_type == TokenType.EXP:
                return Number(left_node) ** Number(right_node)
            elif node.op_tok.token_type == TokenType.N_EQ:
                return Number(left_node != right_node)
            elif node.op_tok.token_type == TokenType.IS_EQ:
                return Number(left_node == right_node)
            elif node.op_tok.token_type == TokenType.LTE:
                return Number(left_node <= right_node)
            elif node.op_tok.token_type == TokenType.GTE:
                return Number(left_node >= right_node)
            elif node.op_tok.token_type == TokenType.LT:
                return Number(left_node < right_node)
            elif node.op_tok.token_type == TokenType.GT:
                return Number(left_node > right_node)
            elif node.op_tok.value == 'and':
                return Number(left_node).anded_by(right_node)
            elif node.op_tok.value == 'or':
                return Number(left_node).ored_by(right_node)

        elif type(left_node).__name__ == 'String' and \
                type(right_node).__name__ == 'String':
            if node.op_tok.token_type == TokenType.PLUS:
                return String(left_node.value) + String(right_node.value)
            elif node.op_tok.token_type == TokenType.MINUS:
                return String(left_node) - String(right_node)
            elif node.op_tok.token_type == TokenType.N_EQ:
                return Number(left_node != right_node)
            elif node.op_tok.token_type == TokenType.IS_EQ:
                return Number(left_node == right_node)
            elif node.op_tok.token_type == TokenType.LTE:
                return Number(left_node <= right_node)
            elif node.op_tok.token_type == TokenType.GTE:
                return Number(left_node >= right_node)
            elif node.op_tok.token_type == TokenType.LT:
                return Number(left_node < right_node)
            elif node.op_tok.token_type == TokenType.GT:
                return Number(left_node > right_node)

        elif (type(left_node).__name__ == 'String' and \
              isinstance(right_node.value, int)) or \
                type(right_node).__name__ == 'String' and \
                isinstance(left_node.value, int):
            if node.op_tok.token_type == TokenType.MULT:
                return String(left_node.value * Number(right_node).value)
        elif type(left_node).__name__ == 'List' and \
            type(right_node).__name__ == 'List':
            if node.op_tok.token_type == TokenType.N_EQ:
                return Number(left_node != right_node)
            elif node.op_tok.token_type == TokenType.IS_EQ:
                return Number(left_node == right_node)
        else:
            return Number(0)

    def visit_UnaryOpNode(self, node: UnaryOpNode, symbol_table: SymbolTable) -> Number:
        """
        Returns the same number or the negative version of said number.

        UnaryOpNode is a node class used for unary operations denoted by -{number} or +{number}
        """
        number = self.visit(node.node, symbol_table)

        if node.op_tok.token_type == TokenType.MINUS:
            return number * Number(-1)
        elif node.op_tok.token_type == TokenType.PLUS:
            return number
        elif node.op_tok.value == 'not':
            return number.notted_by()

    def visit_VarAssignNode(self, node: VarAssignNode, symbol_table: SymbolTable) -> None:
        """
        Assigns a variable in the symbol table

        VarAssignNode is a node class used for the assignment of a variable, denoted by 'identifier = value'.
        """
        assignment = self.visit(node.value, symbol_table)

        symbol_table[node.name] = assignment

    def visit_VarAccessNode(self, node: VarAccessNode, symbol_table: SymbolTable) -> Union[Number, String]:
        """
        Returns the value of a variable in the symbol table.

        VarAccessNode is a node class used for getting the value of a certain variable, denoted by 'identifier'.
        """
        try:
            res = symbol_table[node.name]
        except KeyError:
            if 'params' in symbol_table.symbols.keys():
                res = symbol_table["params"][node.name]
            elif symbol_table != self.symbol_table:
                res = self.symbol_table[node.name]

        return res

    def visit_list(self, list_to_visit: list, symbol_table: SymbolTable) -> Number:
        """
        The visit_list method is for visiting logical expressions,
        containing things like <, >, <=, >=, and, or, not, etc.
        """
        passed_cases = []
        for node in list_to_visit:
            result = self.visit(node, symbol_table)
            passed_cases.append(result)

        if False in [num.value == 1 for num in passed_cases]:
            return self.symbol_table["false"]
        else:
            return self.symbol_table["true"]

    def visit_IfNode(self, node: IfNode, symbol_table: SymbolTable) -> Union[List, ReturnNode]:
        """
        Interprets an if statement.

        IfNode is a node class used for if statements, with the optional elif and else statements following it.
        """
        for case in node.cases:
            condition = case[0]
            passed_cases = []
            for idx, cond in enumerate(condition):
                result = self.visit(cond, symbol_table)
                passed_cases.append(result)
            expr = case[-1]
            if False in [num.value == 1 for num in passed_cases]:
                pass
            else:
                block_results = []
                for line in [elem for elem in expr if elem is not None]:
                    if isinstance(line, ReturnNode):
                        return line
                    res = self.visit(line, symbol_table)
                    block_results.append(res)
                return block_results

        if node.else_case:
            expr = node.else_case

            block_results = []
            for line in [elem for elem in expr if elem is not None]:
                if isinstance(line, ReturnNode):
                    return line
                res = self.visit(line, symbol_table)
                block_results.append(res)

            return block_results
