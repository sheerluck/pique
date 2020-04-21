"""
logGroups.[*].(name in [1, 2, 3])
logGroups.[*].{logGroupName,storedBytes}.(storedBytes > 1000000)
logGroups.[*].(storedBytes > 1000000).{logGroupName,storedBytes}
Things.[*].{foo,bar,baz:'chuzzle'}.(bar in 1, 2, 3)

sum()

builtin_func3()

logGroups.(sort(IT))

People.(len(IT)) ->
12


# -----------
# THIS IS WRONG:
Person.(len(IT.name)) ->
23

# IT SHOULD BE:
Person.(len(name)) ->
23
# Because the `IT` should only be used for the toplevel object, not keys
Person.Contacts.(sort(IT))

# -----------

{"name" : "Pebaz"}
Person.(assign(name, name * 2)) ->  ALSO: Person.{"name" : name * 2}
    <- "name" is there because `name` is bound to the object key
{
    "name": "PebazPebaz"
}

[1, 2, 3, 4]
Array.(len(IT)) ->
4

[1, 2, 3, 4]
Array.{"len" : len(IT)} ->
{
    "len": 4
}

Support Slice Objects:
Array.foo.[1:-3:2]

someobject[slice(*("[1:-3:2]".split(':')))]


[integer] (Python) {Python, Pyhon : Python}

( print( "))))" ) ).this.[0].not.valid.python.{}
"""


# NOTE: CREATE AN assign() FUNCTION THAT CAN ASSIGN WITHIN AN EXPRESSION
# NOTE: USE A STDLIB FUNCTION TO PARSE EXPRESSIONS FOR PROPER SYNTAX.
# NOTE: DON'T USE A STATE MACHINE. MAKE PASSES FOR EACH PAREN COMBO
# NOTE: IF YOU COME TO A DOT AND THE PAREN IS MATCHED, ITS DONE.

import sys, json, ast
from pique.cli import parser


class Query:
    "Base class for all queries"

class SelectKey(Query):  # some-key | `some-key` | some key
    "Narrow down data"

class BuildObject(Query):  # {}
    "Filter or enhance data"

class Index(Query):  # []
    "Index an object or an array"

    def __init__(self, source):
        if ':' in source:
            index = slice(*map(int, source.split(':')))
        else:
            index = int(source)

class Expression(Query):  # ()
    "Query an object using a Python expression"


def parse_query_string(query_string: str) -> list:
    "Parses out each query string into its own string"

    # "logGroups.[*].(storedBytes.foo.bar > 1000000).{logGroupName,storedBytes}"

    print()
    print(query_string)
    print()

    query_string += '.'

    def choose_state(char):
        state_map = {
            '[' : 'index',
            '{' : 'build',
            '(' : 'query'
        }
        if char in state_map:
            return state_map[char]
        else:
            return 'select'

    state = choose_state(query_string[0])
    stack = []
    groups = []
    active_brace = False
    index = 0

    opposite = {
        '[' : ']',
        '(' : ')',
        '{' : '}',
        ']' : '[',
        '}' : '{',
        ')' : '('
    }

    for i in range(1, len(query_string)):
        char = query_string[i]

        # Handle EOL and group submission, regardless of state
        if char == '.' and not stack:
            groups.append(query_string[index:i])
            index = i + 1
            if i < len(query_string) - 1:
                state = choose_state(query_string[i + 1])
            continue

        elif char in '[{(':
            # First ever brace
            if not stack:
                # May be able to change to: stack = ['(', ')']
                stack.append(char)

            # Matching brace
            elif stack[-1] == opposite[char]:
                stack.append(char)

            else:
                pass

        elif char in ']})':
            if stack[-1] in '[{(':
                stack.pop()

            elif stack[-1] == opposite[char]:
                stack.pop()

            else:
                pass

    if stack:
        "Something went wrong..."

    return groups


def build_query(query_list: list) -> list:
    "Build a list of queries to run on a given data set"
    return []


def query(data: dict, query_string: str) -> dict:
    """
    """


def main(args: list=[]) -> int:
    "Run pq to query JSON data from CLI"
    args = args or sys.argv[1:]

    cli = parser.parse_args(args)

    print(cli)
    print(parse_query_string(cli.query))

    return 0


def is_valid_python_code(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def main(args):
    #query = '(  print("))))".strip())  ).this.[0].not.valid.python.{}'
    query = ''.join(sys.argv[1:]) or '(a.b.c).(lm().nop()).().[-1].[*].[1:-1].{foo}.{foo,bar}.{"whoa" : {"name":"Pebaz"}}.{foo : 123, bar}.name.person\.age.`|^^%$#`'

    print('---------------------')
    print(query)

    DOT, PAREN, SQUARE, BRACE, KEY = 'DOT PAREN SQUARE BRACE KEY'.split()
    commands = []
    state = DOT
    paren_buf = ''
    brace_key_list = []
    query_it = iter(query)

    for i in query_it:
        #print(state)
        if state == DOT:
            #print('->', DOT)
            if i == '.':
                continue
            elif i == '(':
                state = PAREN
            elif i == '[':
                state = SQUARE
            elif i == '{':
                state = BRACE
            else:
                paren_buf += i
                state = KEY
                #raise Exception(f'Should never get here: i = {i}')

        elif state == PAREN:
            #print('->', PAREN, paren_buf)
            if i == ')' and is_valid_python_code(paren_buf.strip()):
                commands.append(f'<PAREN: {repr(paren_buf.strip())}>')
                paren_buf = ''
                state = DOT
            else:
                paren_buf += i

        elif state == SQUARE:
            stripped = paren_buf.strip()
            if i == ']':
                if (is_valid_python_code(stripped) or stripped == '*'):
                    commands.append(f'<SQUARE: {repr(stripped)}>')
                    paren_buf = ''
                    state = DOT
                elif ':' in stripped:
                    try:
                        commands.append(f'<SQUARE: {repr(stripped)}>')
                        paren_buf = ''
                        state = DOT
                    except:
                        raise Exception('Invalid Syntax')
                else:
                    raise Exception('Invalid Syntax')
            else:
                paren_buf += i

        elif state == BRACE:
            if i in '},:' and is_valid_python_code(paren_buf.strip()):
                brace_key_list.append(paren_buf.strip())
                paren_buf = ''
                if i == ':':
                    brace_key_list.append(':')
                elif i == '}':
                    commands.append(f'<BRACE: {repr(brace_key_list)}>')
                    brace_key_list.clear()
                    state = DOT
            else:
                paren_buf += i

        elif state == KEY:
            if i == '\\':
                paren_buf += next(query_it)
            elif i == '.':
                commands.append(f'<KEY: {repr(paren_buf)}>')
                paren_buf = ''
                state = DOT
            else:
                paren_buf += i

    # It is possible to be in the KEY state after loop exit
    if state == KEY:
        commands.append(f'<KEY: {repr(paren_buf)}>')

    print(paren_buf)
    print('[')
    for c in commands:
        print('   ', c)
    print(']')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

