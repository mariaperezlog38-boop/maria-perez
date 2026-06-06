import unittest

from calculadora_bcv_logic import (
    clean_rate,
    convert_amount,
    format_result,
    parse_amount,
)


class TestCalculadoraBCVLogic(unittest.TestCase):
    def test_parse_amount_valid(self):
        self.assertEqual(parse_amount("123.45"), 123.45)
        self.assertEqual(parse_amount("  99,99 "), 99.99)

    def test_parse_amount_empty(self):
        with self.assertRaises(ValueError):
            parse_amount("")

    def test_parse_amount_invalid(self):
        with self.assertRaises(ValueError):
            parse_amount("abc")

    def test_convert_amount_usd_to_bs(self):
        self.assertAlmostEqual(convert_amount(10, 30.5, "USD a Bs"), 305.0)

    def test_convert_amount_bs_to_usd(self):
        self.assertAlmostEqual(convert_amount(305.0, 30.5, "Bs a USD"), 10.0)

    def test_convert_amount_invalid_mode(self):
        with self.assertRaises(ValueError):
            convert_amount(100, 25.0, "EUR a Bs")

    def test_convert_amount_negative(self):
        with self.assertRaises(ValueError):
            convert_amount(-1, 25.0, "USD a Bs")

    def test_convert_amount_zero_rate(self):
        with self.assertRaises(ValueError):
            convert_amount(10, 0, "USD a Bs")

    def test_format_result_usd_to_bs(self):
        self.assertEqual(format_result(305.0, "USD a Bs"), "305.00 Bs")

    def test_format_result_bs_to_usd(self):
        self.assertEqual(format_result(10.0, "Bs a USD"), "10.00 USD")

    def test_clean_rate(self):
        self.assertEqual(clean_rate("Bs. 30.500,00"), 30500.00)


if __name__ == "__main__":
    unittest.main()
