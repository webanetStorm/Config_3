import re
import sys
import tomli as toml
import tomli_w as toml
from typing import Any, Dict


class SyntaxError(Exception):
    pass


def parse_line(line: str, constants: Dict[str, Any]) -> Any:
    line = line.strip()
    if line.startswith('"'):
        return None
    elif ':=' in line:
        name, value = map(str.strip, line.split(':=', 1))
        constants[name] = parse_value(value, constants)
        return None
    elif line.startswith('?{') and line.endswith('}'):
        const_name = line[2:-1].strip()
        if const_name not in constants:
            raise SyntaxError(f'Undefined constant: {const_name}')
        return constants[const_name]
    elif line.startswith('table([') and line.endswith('])'):
        return parse_table(line[7:-2].strip(), constants)
    else:
        raise SyntaxError(f'Unknown syntax: {line}')

def parse_table(content: str, constants: Dict[str, Any]) -> Dict[str, Any]:
    table = {}
    for entry in content.split(','):
        if '=' not in entry:
            raise SyntaxError(f'Invalid table entry: {entry}')
        key, value = map(str.strip, entry.split('=', 1))
        table[key] = parse_value(value, constants)
    return table

def parse_value(value: str, constants: Dict[str, Any]) -> Any:
    if value.isdigit():
        return int(value)
    elif value.startswith('table([') and value.endswith('])'):
        return parse_table(value[7:-2].strip(), constants)
    elif value.startswith('?{') and value.endswith('}'):
        return parse_line(value, constants)
    else:
        raise SyntaxError(f'Invalid value: {value}')

def main():
    constants = {}
    result = {}

    try:
        print('Enter configuration input. Press Ctrl+D to finish:')
        input_lines = sys.stdin.read().splitlines()
        for line in input_lines:
            parsed = parse_line(line, constants)
            if isinstance(parsed, dict):
                result.update(parsed)

        print(toml.dumps(result))
    except SyntaxError as e:
        print(f'Syntax error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
