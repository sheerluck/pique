# To get JSON, run this command:
# aws pinpoint phone-number-validate --region us-east-1 --number-validate-request PhoneNumber=525536747273 | python3 poc.py NumberValidateResponse
# cat input.json | python3 poc.py "Things.[*].inventory.[1]"
# aws logs describe-log-groups | python3 poc.py "logGroups.[*].logGroupName.(= '/pbz/test-log-group')"
# Using [*] always creates an array. Can I use {} to build custom objects?
# aws logs describe-log-groups | python3 poc.py "logGroups.[*].(> storedBytes 0).{logGroupName,storedBytes}"
# Count: "logGroups.!count"
# Ranges: "logGroups.[2:4]"
# aws logs describe-log-groups | python3 poc.py "logGroups.[*].{logGroupName,storedBytes}.(> storedBytes 1000000)"

# Raw Python syntax now works: aws lambda list-functions | python3 poc.py "Functions.[*].(Timeout > 3).Timeout"

"logGroups.[*].(name in [1, 2, 3])"
"logGroups.[*].{logGroupName,storedBytes}.(storedBytes > 1000000)"

"Things.[*].{foo,bar,baz:'chuzzle'}.(bar in 1, 2, 3)"

import sys, json

def parse_commands(string):
    cmds = []
    for cmd in string.split('.'):
        # Index
        if cmd.startswith('['):
            cmd = cmd[1:-1]
            if cmd[0] != '*':
                cmd = int(cmd)

        # Logic expression
        #elif cmd.startswith('('):
        #    cmd = cmd[1:-1]
        
        cmds.append(cmd)
    return cmds

def drilldown(data, commands):
    for i in range(len(commands)):
        cmd = commands[i]
        if cmd == '*':
            data = [drilldown(element, commands[i + 1:]) for element in data]
            break

        elif not isinstance(cmd, int) and cmd.startswith('('):
            "logGroups.[*].{logGroupName,storedBytes}.(storedBytes > 1000000)"
            cmd = cmd[1:-1]
            static_data = data.copy()
            if not eval(cmd, {}, static_data):
                return None
            return drilldown([static_data], commands[i + 1:])
            '''
            data = [
                drilldown(element, commands[i + 1:])
                for element in data
                if eval(cmd, static_data)
            ]
            '''

        elif not isinstance(cmd, int) and cmd.startswith('{'):
            cmd = cmd[1:-1]  # Unwrap from {}
            obj_keys = cmd.split(',')
            data = {key : data[key] for key in obj_keys}

        # Logic Expression
        elif not isinstance(cmd, int) and cmd.startswith('='):
            op, comparison_key, arg = cmd.split()

            # Parse it into it's data type
            arg = eval(arg)

            # sys.stdin = open('/dev/tty')
            # import pdb; pdb.set_trace()

            if data[comparison_key] != arg:
                return None
            
            #data = [drilldown(element, commands[i + 1:]) for element in data]

        elif not isinstance(cmd, int) and cmd.startswith('>'):
            op, comparison_key, arg = cmd.split()
            arg = eval(arg)

            if not (data[comparison_key] > arg):
                return None
        
        else:
            data = data[cmd]
    
    if isinstance(data, list):
        data = [i for i in data if i]
    return data


data = json.loads(sys.stdin.read())
if len(sys.argv) > 1:
    result = drilldown(data, parse_commands(sys.argv[1]))
else:
    result = data


from pygments.style import Style
from pygments.token import *

# http://www.1728.org/colrchr6.htm
class IcyKiss(Style):
    default_style = ''
    styles = {
        Name: '#b2b',
        String: '#7bd',
        Number: '#07d',
        Keyword: 'bold #b0b'
    }

class Python3(Style):
    default_style = ''
    styles = {
        Name: '#07c',
        String: '#fc4',
        Number: '#4cf',
        Keyword: 'bold #fc4'
    }

class Allovelle(Style):
    default_style = ''
    styles = {
        Name: '#f0a',
        #String: '#fff',
        Number: '#fc4',
        Keyword: 'bold #f4a'
    }

class Haelyon(Style):
    default_style = ''
    styles = {
        Name: '#39b',
        String: '#3ab',
        Number: '#f05',
        Keyword: 'bold #888'
    }

class Wing(Style):
    default_style = ''
    styles = {
        Name: '#fc1',
        String: '#bbb',
        #Number: '#fff',
        Keyword: 'bold #bbb'
    }

class Spire(Style):
    default_style = ''
    styles = {
        Name: '#bd2',
        String: '#fb1',
        Number: '#1bf',
        Keyword: 'bold #f05'
    }

formatted_json = json.dumps(result, indent=4)

from pygments import highlight, lexers, formatters
import sys

# If in pipe, don't print console colors, just print text
if sys.stdout.isatty():
    print(highlight(
        formatted_json,
        lexers.JsonLexer(),
        formatters.Terminal256Formatter(style=Python3)
    ))
else:
    print(formatted_json)
