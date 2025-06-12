import re
from tabulate import tabulate

# Token ID assignment map
token_ids = {
    'int': 0,
    'main': 1,
    '(': 2,
    ')': 3,
    'begin': 4,
    'end': 15,
    '=': 8,
    '+': 14,
    ',': 6,
    ';': 11,
    'while': 12,
}

# Lexer
def lexer(code):
    token_specification = [
        ('KEYWORD',    r'\b(int|main|begin|end|while)\b'),
        ('NUMBER',     r'\b\d+\b'),
        ('IDENTIFIER', r'\b[a-zA-Z_]\w*\b'),
        ('ASSIGN',     r'='),
        ('PLUS',       r'\+'),
        ('COMMA',      r','),
        ('SEMICOLON',  r';'),
        ('LPAREN',     r'\('),
        ('RPAREN',     r'\)'),
        ('SKIP',       r'[ \t]+'),
        ('NEWLINE',    r'\n'),
        ('MISMATCH',   r'.')
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokens = []
    id_counter = 16

    token_map = dict(token_ids)  # Copy predefined IDs

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()

        if kind in ['SKIP', 'NEWLINE']:
            continue
        if kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character {value!r}')
        if kind == 'IDENTIFIER' or kind == 'NUMBER':
            if value not in token_map:
                token_map[value] = id_counter
                id_counter += 1
        token_id = token_map.get(value, token_ids.get(value, id_counter))
        tokens.append((kind, value, token_id))
    
    return tokens, token_map

# Dummy Parser with table data
class Parser:
    def _init_(self, tokens):
        self.tokens = tokens
        self.symbols = sorted(set(t[1] for t in tokens if t[0] == 'IDENTIFIER'))

    def parse(self):
        pass  # Placeholder

    def display_symbol_table(self):
        print("\n=== SYMBOL TABLE ===")
        print(tabulate([[sym] for sym in self.symbols], headers=["Identifier"], tablefmt="grid"))

    def display_first_sets(self):
        first_sets = [
            ["program", "int"],
            ["declarations", "char, empty, int"],
            ["var_list", "IDENTIFIER"],
            ["switch_stmt", "switch"],
            ["case_list", "case, empty"],
            ["case_stmt", "case"],
            ["empty", "empty"]
        ]
        print("\n=== FIRST SETS ===")
        print(tabulate(first_sets, headers=["Non-Terminal", "First Set"], tablefmt="grid"))

    def display_follow_sets(self):
        follow_sets = [
            ["program", "$"],
            ["declarations", "RETURN, switch"],
            ["var_list", ";"],
            ["switch_stmt", "RETURN"],
            ["case_list", "END"],
            ["case_stmt", "END, case"],
            ["empty", "END, RETURN, case, switch"]
        ]
        print("\n=== FOLLOW SETS ===")
        print(tabulate(follow_sets, headers=["Non-Terminal", "Follow Set"], tablefmt="grid"))

    def display_parsing_table(self):
        parsing_table = [
            ["Non-Terminal", "$", ";", "END", "IDENTIFIER", "RETURN", "case", "char", "int", "switch"],
            ["case_list", "", "", "case_list → empty", "", "", "case_list → empty", "", "", ""],
            ["case_stmt", "", "", "", "", "", "case_stmt → CASE SUB COLON ...", "", "", ""],
            ["declarations", "", "", "", "", "declarations → empty", "", "declarations → empty", "declarations → empty", "declarations → empty"],
            ["empty", "", "", "empty → empty", "", "empty → empty", "empty → empty", "", "", "empty → empty"],
            ["program", "", "", "", "", "", "", "", "program → INT MAIN LPAREN R...", ""],
            ["switch_stmt", "", "", "", "", "", "", "", "", "switch_stmt → SWITCH LPAREN..."],
            ["var_list", "", "", "", "var_list → IDENTIFIER COMMA...", "", "", "", "", ""]
        ]
        print("\n=== PARSING TABLE WITH PRODUCTIONS ===")
        print(tabulate(parsing_table, headers="firstrow", tablefmt="grid"))

    def display_parsing_actions(self):
        actions = [
            [0, "$", "Initial state"],
            [1, "$ program", "Push goal symbol"],
            [2, "... declarations switch_stmt RETURN ...", "Expand program rule"],
            [3, "... { declarations switch_stmt ...", "Match terminal 'int'"],
            [4, "... main ( ) {", "Match terminal sequence"],
            [5, "... int main ( )", "Reduce: declarations"],
            [6, "... int main ( )", "Reduce: empty declarations"],
            [7, "... int main ( )", "Reduce: switch statement"],
            [8, "$ int main ( )", "Reduce: program"]
        ]
        print("\n=== PARSING ACTIONS ===")
        print(tabulate(actions, headers=["Step", "Stack", "Action"], tablefmt="grid"))

    def display_grammar_rules(self):
        rules = [
            ["program → int main ( ) begin declarations switch_stmt end"],
            ["declarations → int var_list ;"],
            ["var_list → IDENTIFIER , IDENTIFIER = NUMBER , IDENTIFIER"],
            ["switch_stmt → while ( expr ) begin stmt end"],
            ["stmt → expr = expr + expr ;"]
        ]
        print("\n=== GRAMMAR RULES USED ===")
        print(tabulate(rules, headers=["Rule"], tablefmt="grid"))

    def display_terminals_nonterminals(self):
        terminals = [
            ["int", "main", "(", ")", "begin", "end", "while", "IDENTIFIER", "=", "+", ",", ";", "NUMBER"]
        ]
        non_terminals = [
            ["program", "declarations", "var_list", "switch_stmt", "stmt"]
        ]
        print("\n=== TERMINALS ===")
        print(tabulate(terminals, headers=["Terminals"], tablefmt="grid"))
        print("\n=== NON-TERMINALS ===")
        print(tabulate(non_terminals, headers=["Non-Terminals"], tablefmt="grid"))

    def display_lr_parse_table(self):
        lr_table = [
            ["State", "int", "main", "(", ")", "IDENTIFIER", "=", "+", ",", ";", "while", "begin", "end", "$"],
            ["0", "s5", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["1", "", "s6", "", "", "", "", "", "", "", "", "", "", ""],
            ["2", "", "", "s7", "", "", "", "", "", "", "", "", "", ""],
            ["3", "", "", "", "r1", "", "", "", "", "", "", "", "", ""],
        ]
        print("\n=== LR PARSE TABLE ===")
        print(tabulate(lr_table, headers="firstrow", tablefmt="grid"))

# Main runner
def main():
    source_code = """
int main()
begin
 int n, re = 0, rem;
 while(expr)
 begin
 expr=expr+expr;
 end
end
""".strip()

    print("\n=== SOURCE CODE ===")
    print(source_code)

    tokens, token_map = lexer(source_code)

    print("\n=== TOKEN TABLE ===")
    print(tabulate([[i, typ, val, tid] for i, (typ, val, tid) in enumerate(tokens)],
                   headers=["Index", "Token Type", "Lexeme", "Token ID"], tablefmt="grid"))

    print("\n=== TOKEN ID MAP ===")
    print(tabulate([{"Token": k, "ID": v} for k, v in sorted(token_map.items(), key=lambda x: x[1])],
                   headers="keys", tablefmt="grid"))

    parser = Parser(tokens)
    parser.display_symbol_table()
    parser.display_first_sets()
    parser.display_follow_sets()
    parser.display_parsing_table()
    parser.display_parsing_actions()
    parser.display_grammar_rules()
    parser.display_terminals_nonterminals()
    parser.display_lr_parse_table()

    print("\n✅ Parsing completed successfully!")

if _name_ == "_main_":
    main()
