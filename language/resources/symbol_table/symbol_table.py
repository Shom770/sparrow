class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def __getitem__(self, item):
        return self.symbols[item]

    def __setitem__(self, key, value):
        self.symbols[key] = value

    def __delitem__(self, key):
        del self.symbols[key]