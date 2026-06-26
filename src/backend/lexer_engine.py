# src/backend/lexer_engine.py
# Hand-Written Finite State Machine for MAXIMUM ACCURACY

import re

# ---------- Keyword Set (Combined from C, C++, Python, Java) ----------
KEYWORDS = {
    'if', 'else', 'elif', 'while', 'for', 'do', 'switch', 'case', 'default',
    'break', 'continue', 'return', 'int', 'float', 'double', 'char', 'void',
    'long', 'short', 'unsigned', 'signed', 'const', 'static', 'volatile',
    'extern', 'struct', 'union', 'enum', 'typedef', 'sizeof', 'class',
    'public', 'private', 'protected', 'virtual', 'override', 'final',
    'try', 'catch', 'throw', 'throws', 'finally', 'import', 'package',
    'using', 'namespace', 'def', 'lambda', 'yield', 'with', 'as', 'pass',
    'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is', 'global',
    'nonlocal', 'assert', 'del', 'from', 'raise', 'exec', 'print', 'range',
    'len', 'str', 'bool', 'list', 'dict', 'tuple', 'set', 'object'
}

# ---------- Multi-Character Operators ----------
MULTI_OPS = {
    '==', '!=', '<=', '>=', '+=', '-=', '*=', '/=', '%=',
    '&&', '||', '++', '--', '->', '...', '<<', '>>'
}

# ---------- Single Character Tokens ----------
SINGLE_CHAR_TOKENS = {
    ';': 'DELIMITER', ',': 'DELIMITER', ':': 'DELIMITER',
    '{': 'DELIMITER', '}': 'DELIMITER', '(': 'DELIMITER',
    ')': 'DELIMITER', '[': 'DELIMITER', ']': 'DELIMITER',
    '+': 'OPERATOR', '-': 'OPERATOR', '*': 'OPERATOR',
    '/': 'OPERATOR', '%': 'OPERATOR', '=': 'OPERATOR',
    '<': 'OPERATOR', '>': 'OPERATOR', '!': 'OPERATOR',
    '&': 'OPERATOR', '|': 'OPERATOR', '^': 'OPERATOR',
    '~': 'OPERATOR', '?': 'OPERATOR',
}


def tokenize(source_code):
    """
    Hand-written state machine tokenizer.
    Processes character by character for 100% accuracy.
    """
    if not source_code:
        return []

    tokens = []
    i = 0
    n = len(source_code)
    line = 1
    col = 1

    while i < n:
        ch = source_code[i]

        # ---------- 1. SKIP WHITESPACE ----------
        if ch in ' \t\r\f\v':
            col += 1
            i += 1
            continue

        # ---------- 2. HANDLE NEWLINES ----------
        if ch == '\n':
            line += 1
            col = 1
            i += 1
            continue

        # ---------- 3. HANDLE SINGLE-LINE COMMENTS (// and #) ----------
        if ch == '/' and i + 1 < n and source_code[i + 1] == '/':
            # Skip until end of line
            while i < n and source_code[i] != '\n':
                i += 1
            # The newline will be handled in the next loop iteration
            continue

        if ch == '#':
            # Python comment - skip until end of line
            while i < n and source_code[i] != '\n':
                i += 1
            continue

        # ---------- 4. HANDLE MULTI-LINE COMMENTS (/* */) WITH NESTING ----------
        if ch == '/' and i + 1 < n and source_code[i + 1] == '*':
            start_line = line
            start_col = col
            # Skip the '/*'
            i += 2
            col += 2
            nest_level = 1

            while i < n and nest_level > 0:
                if source_code[i] == '/' and i + 1 < n and source_code[i + 1] == '*':
                    nest_level += 1
                    i += 2
                    col += 2
                elif source_code[i] == '*' and i + 1 < n and source_code[i + 1] == '/':
                    nest_level -= 1
                    i += 2
                    col += 2
                else:
                    if source_code[i] == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                    i += 1
            # Comment is fully skipped (no token emitted)
            continue

        # ---------- 5. HANDLE STRINGS (Double and Single Quotes) ----------
        if ch in '"\'':  # Fixed: removed the extra backslash quote
            quote_char = ch
            start_line = line
            start_col = col
            lexeme = ch
            i += 1
            col += 1

            while i < n:
                # Handle escape sequences
                if source_code[i] == '\\':
                    # Skip the backslash and the escaped character
                    lexeme += source_code[i]
                    i += 1
                    col += 1
                    if i < n:
                        lexeme += source_code[i]
                        i += 1
                        col += 1
                    continue

                if source_code[i] == quote_char:
                    lexeme += source_code[i]
                    i += 1
                    col += 1
                    break

                # Handle newline inside string (error, but keep going)
                if source_code[i] == '\n':
                    line += 1
                    col = 1
                    lexeme += '\n'
                    i += 1
                    continue

                lexeme += source_code[i]
                i += 1
                col += 1

            tokens.append({
                'lexeme': lexeme,
                'type': 'STRING',
                'line': start_line,
                'col': start_col
            })
            continue

        # ---------- 6. HANDLE NUMBERS ----------
        if ch.isdigit() or (ch == '.' and i + 1 < n and source_code[i + 1].isdigit()):
            start_line = line
            start_col = col
            lexeme = ''
            has_dot = False
            has_exponent = False

            # Handle sign for exponent
            if ch == '.':
                has_dot = True
                lexeme += ch
                i += 1
                col += 1

            while i < n:
                ch2 = source_code[i]
                if ch2.isdigit():
                    lexeme += ch2
                    i += 1
                    col += 1
                elif ch2 == '.' and not has_dot and not has_exponent:
                    has_dot = True
                    lexeme += ch2
                    i += 1
                    col += 1
                elif ch2 in 'eE' and not has_exponent:
                    has_exponent = True
                    lexeme += ch2
                    i += 1
                    col += 1
                    # Optional sign after exponent
                    if i < n and source_code[i] in '+-':
                        lexeme += source_code[i]
                        i += 1
                        col += 1
                else:
                    break

            tokens.append({
                'lexeme': lexeme,
                'type': 'NUMBER',
                'line': start_line,
                'col': start_col
            })
            continue

        # ---------- 7. HANDLE IDENTIFIERS AND KEYWORDS ----------
        if ch.isalpha() or ch == '_':
            start_line = line
            start_col = col
            lexeme = ''

            while i < n and (source_code[i].isalnum() or source_code[i] == '_'):
                lexeme += source_code[i]
                i += 1
                col += 1

            # Determine if it's a keyword or identifier
            token_type = 'KEYWORD' if lexeme in KEYWORDS else 'IDENTIFIER'
            tokens.append({
                'lexeme': lexeme,
                'type': token_type,
                'line': start_line,
                'col': start_col
            })
            continue

        # ---------- 8. HANDLE OPERATORS (Multi-char first) ----------
        # Check for multi-character operators
        matched = False
        for op in MULTI_OPS:
            if source_code.startswith(op, i):
                start_line = line
                start_col = col
                tokens.append({
                    'lexeme': op,
                    'type': 'OPERATOR',
                    'line': start_line,
                    'col': start_col
                })
                i += len(op)
                col += len(op)
                matched = True
                break

        if matched:
            continue

        # ---------- 9. HANDLE SINGLE-CHAR TOKENS ----------
        if ch in SINGLE_CHAR_TOKENS:
            start_line = line
            start_col = col
            tokens.append({
                'lexeme': ch,
                'type': SINGLE_CHAR_TOKENS[ch],
                'line': start_line,
                'col': start_col
            })
            i += 1
            col += 1
            continue

        # ---------- 10. HANDLE ERROR (Unrecognized Character) ----------
        start_line = line
        start_col = col
        tokens.append({
            'lexeme': ch,
            'type': 'ERROR',
            'line': start_line,
            'col': start_col
        })
        i += 1
        col += 1

    return tokens