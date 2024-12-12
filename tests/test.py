import unittest
from io import StringIO
from unittest.mock import patch
from main import main, parse_line, parse_value, parse_table, SyntaxError

class TestConfigParser(unittest.TestCase):

    def test_parse_value_integer(self):
        constants = {}
        self.assertEqual(parse_value("123", constants), 123)

    def test_parse_value_table(self):
        constants = {}
        value = "table([key1 = 123, key2 = 456])"
        expected = {"key1": 123, "key2": 456}
        self.assertEqual(parse_value(value, constants), expected)

    def test_parse_value_constant_reference(self):
        constants = {"MY_CONSTANT": 42}
        self.assertEqual(parse_value("?{MY_CONSTANT}", constants), 42)

    def test_parse_value_invalid_reference(self):
        constants = {}
        with self.assertRaises(SyntaxError):
            parse_value("?{UNKNOWN_CONSTANT}", constants)

    def test_parse_value_invalid_syntax(self):
        constants = {}
        with self.assertRaises(SyntaxError):
            parse_value("invalid_syntax", constants)

    def test_parse_table_valid(self):
        constants = {}
        content = "key1 = 123, key2 = 456"
        expected = {"key1": 123, "key2": 456}
        self.assertEqual(parse_table(content, constants), expected)

    def test_parse_table_invalid_entry(self):
        constants = {}
        with self.assertRaises(SyntaxError):
            parse_table("key1 123, key2 = 456", constants)

    def test_parse_line_constant_definition(self):
        constants = {}
        parse_line("MY_CONSTANT := 123", constants)
        self.assertIn("MY_CONSTANT", constants)
        self.assertEqual(constants["MY_CONSTANT"], 123)

    def test_parse_line_table_definition(self):
        constants = {}
        result = parse_line('table([key1 = 123, key2 = 456])', constants)
        expected = {"key1": 123, "key2": 456}
        self.assertEqual(result, expected)

    def test_parse_line_constant_reference(self):
        constants = {"MY_CONSTANT": 42}
        result = parse_line("?{MY_CONSTANT}", constants)
        self.assertEqual(result, 42)

    def test_parse_line_unknown_syntax(self):
        constants = {}
        with self.assertRaises(SyntaxError):
            parse_line("unknown_syntax", constants)

    def test_integration_valid_input(self):
        constants = {}
        input_data = [
            'MY_CONSTANT := 42',
            'table([key1 = 123, key2 = ?{MY_CONSTANT}])'
        ]
        result = {}
        for line in input_data:
            parsed = parse_line(line, constants)
            if isinstance(parsed, dict):
                result.update(parsed)
        self.assertEqual(constants, {"MY_CONSTANT": 42})
        self.assertEqual(result, {"key1": 123, "key2": 42})

    def test_integration_invalid_constant(self):
        constants = {}
        input_data = [
            'table([key1 = 123, key2 = ?{MY_CONSTANT}])'
        ]
        with self.assertRaises(SyntaxError):
            for line in input_data:
                parse_line(line, constants)

    @patch('sys.stdin', new_callable=StringIO)
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_valid_input(self, mock_stdout, mock_stdin):
        mock_stdin.write('MY_CONSTANT := 42\n')
        mock_stdin.write('table([key1 = 123, key2 = ?{MY_CONSTANT}])\n')
        mock_stdin.seek(0)
        main()  # Call the main function directly
        result = mock_stdout.getvalue().strip()
        self.assertIn('key1 = 123', result)
        self.assertIn('key2 = 42', result)

    @patch('sys.stdin', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_invalid_input(self, mock_stderr, mock_stdin):
        mock_stdin.write('INVALID_LINE\n')
        mock_stdin.seek(0)
        with self.assertRaises(SystemExit) as exit_code:
            main()
        self.assertEqual(exit_code.exception.code, 1)
        error_message = mock_stderr.getvalue().strip()
        self.assertIn('Syntax error: Unknown syntax', error_message)


if __name__ == '__main__':
    unittest.main()
