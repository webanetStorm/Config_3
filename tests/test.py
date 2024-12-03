import unittest
import subprocess

class TestConfigurationParser(unittest.TestCase):
    def run_parser(self, input_data):
        """Запускает парсер с указанными входными данными."""
        process = subprocess.run(
            ["python", "main.py"],  # Замените на путь к вашему скрипту
            input=input_data,
            text=True,
            capture_output=True,
            encoding='utf-8'  # Явно указать кодировку
        )
        return process

    def test_single_line_comments(self):
        input_data = '" This is a comment\nx := 42\n'
        expected_output = "x = 42\n"
        process = self.run_parser(input_data)
        self.assertEqual(process.stdout.strip(), expected_output)
        self.assertEqual(process.returncode, 0)

    def test_constants(self):
        input_data = "a := 10\nb := 20\nc := ?{a} + ?{b}\n"
        expected_output = "a = 10\nb = 20\nc = 30\n"
        process = self.run_parser(input_data)
        self.assertEqual(process.stdout.strip(), expected_output)
        self.assertEqual(process.returncode, 0)

    def test_nested_tables(self):
        input_data = """
        table([
            key1 = 10,
            key2 = table([
                nested_key1 = 20,
                nested_key2 = 30
            ])
        ])
        """
        expected_output = """
        [table]
        key1 = 10

        [table.key2]
        nested_key1 = 20
        nested_key2 = 30
        """.strip()
        process = self.run_parser(input_data)
        self.assertEqual(process.stdout.strip(), expected_output)
        self.assertEqual(process.returncode, 0)

    def test_invalid_syntax(self):
        input_data = "table([key1, 10])\n"  # Ошибочная строка
        process = self.run_parser(input_data)
        self.assertNotEqual(process.returncode, 0)  # Ожидаем ненулевой код завершения
        self.assertIn("Syntax error", process.stderr)

    def test_complex_configuration(self):
        input_data = """
        a := 42
        b := table([
            key1 = ?{a},
            key2 = table([
                nested = 99
            ])
        ])
        """
        expected_output = """
        a = 42

        [b]
        key1 = 42

        [b.key2]
        nested = 99
        """.strip()
        process = self.run_parser(input_data)
        self.assertEqual(process.stdout.strip(), expected_output)
        self.assertEqual(process.returncode, 0)


if __name__ == "__main__":
    unittest.main()
