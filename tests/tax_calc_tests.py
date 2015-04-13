#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from decimal import Decimal
from docs.tax_calc import *


class TestItem(unittest.TestCase):
    input_tax_exempt = "1 book at 12.49\n"
    input_no_trailing_newline = "1 book at 12.49"
    input_decimal_amount = "1.5 book at 12.49\n"
    input_imported = "1 imported bottle of perfume at 27.99\n"
    input_multiple = "2 imported bottle of perfume at 27.99\n"
    input_invalid_quantity = "-2 imported bottle of perfume at 27.99\n"
    input_invalid_price = "2 imported bottle of perfume at -27.99\n"
    input_malformed = "dfasg<shdga<dssfhadfsgx gsg dfsg"
    input_utf8 = u"1 book about the letter äääääää at 12.49\n"

    def test_item_sunny_day_tax_exempt(self):
        item = Item(self.input_tax_exempt)
        self.assertEqual(item.quantity, Decimal('1'))
        self.assertEqual(item.unit_price, Decimal('12.49'))
        self.assertEqual(item.tax_exempt, True)
        self.assertEqual(item.imported, False)
        self.assertEqual(str(item), "1 book: 12.49")

    def test_item_sunny_day_imported(self):
        item = Item(self.input_imported)
        self.assertEqual(item.quantity, Decimal('1'))
        self.assertEqual(item.unit_price, Decimal('27.99'))
        self.assertEqual(item.tax_exempt, False)
        self.assertEqual(item.imported, True)
        self.assertEqual(str(item), "1 imported bottle of perfume: 32.19")

    def test_item_sunny_day_multiple(self):
        item = Item(self.input_multiple)
        self.assertEqual(item.quantity, Decimal('2'))
        self.assertEqual(item.unit_price, Decimal('27.99'))
        self.assertEqual(item.tax_exempt, False)
        self.assertEqual(item.imported, True)
        self.assertEqual(str(item), "2 imported bottle of perfume: 64.38")

    def test_item_sunny_day_no_trailing_newline(self):
        item = Item(self.input_no_trailing_newline)
        self.assertEqual(item.quantity, Decimal('1'))
        self.assertEqual(item.unit_price, Decimal('12.49'))
        self.assertEqual(item.tax_exempt, True)
        self.assertEqual(item.imported, False)
        self.assertEqual(str(item), "1 book: 12.49")

    def test_item_sunny_day_decimal_amount(self):
        item = Item(self.input_decimal_amount)
        self.assertEqual(item.quantity, Decimal('1.5'))
        self.assertEqual(item.unit_price, Decimal('12.49'))
        self.assertEqual(item.tax_exempt, True)
        self.assertEqual(item.imported, False)
        self.assertEqual(str(item), "1.5 book: 18.74")

    # Cart should not be able to feed None into Item
    def test_item_from_none(self):
        with self.assertRaisesRegexp(AttributeError, "'NoneType' object has no attribute 'strip'"):
            item = Item(None)

    def test_item_from_empty(self):
        with self.assertRaisesRegexp(ValueError, "Input is not well-formed. Items should take the form of a single line containing a quantity, name of the item, the word 'at' then the price"):
            item = Item("")

    def test_item_from_blank(self):
        with self.assertRaisesRegexp(ValueError, "Input is not well-formed. Items should take the form of a single line containing a quantity, name of the item, the word 'at' then the price"):
            item = Item("\t\n ")

    def test_item_invalid_price(self):
        with self.assertRaisesRegexp(ValueError, "Price of items cannot be negative"):
            item = Item(self.input_invalid_quantity)

    def test_item_invalid_price(self):
        with self.assertRaisesRegexp(ValueError, "Price of items cannot be negative"):
            item = Item(self.input_invalid_price)

    def test_item_malformed(self):
        with self.assertRaisesRegexp(ValueError, "Input is not well-formed. Items should take the form of a single line containing a quantity, name of the item, the word 'at' then the price"):
            item = Item(self.input_malformed)

    def test_item_utf8(self):
        item = Item(self.input_utf8)
        self.assertEqual(item.quantity, Decimal('1'))
        self.assertEqual(item.unit_price, Decimal('12.49'))
        self.assertEqual(item.tax_exempt, True)
        self.assertEqual(item.imported, False)
        self.assertEqual(
            unicode(item), u"1 book about the letter äääääää: 12.49")

    def test_get_tax_rate_imported(self):
        item = Item(self.input_imported)
        item.imported = True
        item.tax_exempt = False
        self.assertEqual(item.get_tax_rate(), Decimal('0.15'))

    def test_get_tax_rate_domestic(self):
        item = Item(self.input_imported)
        item.imported = False
        item.tax_exempt = False
        self.assertEqual(item.get_tax_rate(), Decimal('0.1'))

    def test_get_tax_rate_imported_exempt(self):
        item = Item(self.input_imported)
        item.imported = True
        item.tax_exempt = True
        self.assertEqual(item.get_tax_rate(), Decimal('0.05'))

    def test_get_tax_rate_domestic_exempt(self):
        item = Item(self.input_imported)
        item.imported = False
        item.tax_exempt = True
        self.assertEqual(item.get_tax_rate(), Decimal('0.00'))

    def test_get_tax_amount(self):
        item = Item(self.input_imported)
        item.imported = True
        item.tax_exempt = False
        self.assertEqual(item.get_tax_amount(), Decimal('4.20'))

    def test_get_tax_amount_multiple(self):
        item = Item(self.input_imported)
        item.quantity = Decimal('2')
        item.imported = True
        item.tax_exempt = False
        self.assertEqual(item.get_tax_amount(), Decimal('8.40'))

    def test_get_tax_amount_zero_price(self):
        item = Item(self.input_imported)
        item.unit_price = Decimal('0')
        item.imported = True
        item.tax_exempt = False
        self.assertEqual(item.get_tax_amount(), Decimal('0'))

    def test_get_tax_amount_zero_quantity(self):
        item = Item(self.input_imported)
        item.quantity = Decimal('0')
        item.imported = True
        item.tax_exempt = False
        self.assertEqual(item.get_tax_amount(), Decimal('0'))

    def test_get_total_price(self):
        item = Item(self.input_imported)
        item.imported = True
        item.tax_exempt = False
        self.assertEqual(item.get_item_price(), Decimal('32.19'))

    def test_get_total_price_multiple(self):
        item = Item(self.input_imported)
        item.quantity = Decimal('2')
        item.imported = True
        item.tax_exempt = False
        self.assertEqual(item.get_item_price(), Decimal('64.38'))

    def test_get_total_price_zero_unit_price(self):
        item = Item(self.input_imported)
        item.unit_price = Decimal('0')
        item.imported = True
        item.tax_exempt = False
        self.assertEqual(item.get_item_price(), Decimal('0'))

    def test_get_total_price_zero_quantity(self):
        item = Item(self.input_imported)
        item.quantity = Decimal('0')
        item.imported = True
        item.tax_exempt = False
        self.assertEqual(item.get_item_price(), Decimal('0'))


class TestCart(unittest.TestCase):
    input1 = "1 book at 12.49\n1 music CD at 14.99\n1 chocolate bar at 0.85"
    input2 = "1 imported box of chocolates at 10.00\n1 imported bottle of perfume at 47.50"
    input3 = "1 imported bottle of perfume at 27.99\n1 bottle of perfume at 18.99\n1 packet of headache pills at 9.75\n1 box of imported chocolates at 11.25"
    input_utf8 = u"1 book at 12.49\n1 music CD at 14.99\n1 chocolate bär at 0.85"
    expectation1 = u'1 book: 12.49\n1 music CD: 16.49\n1 chocolate bar: 0.85\nSales Taxes: 1.50\nTotal: 29.83\n'
    expectation2 = u'1 imported box of chocolates: 10.50\n1 imported bottle of perfume: 54.65\nSales Taxes: 7.65\nTotal: 65.15\n'
    expectation3 = u'1 imported bottle of perfume: 32.19\n1 bottle of perfume: 20.89\n1 packet of headache pills: 9.75\n1 box of imported chocolates: 11.85\nSales Taxes: 6.70\nTotal: 74.68\n'
    expectation_utf8 = u'1 book: 12.49\n1 music CD: 16.49\n1 chocolate b\xe4r: 0.85\nSales Taxes: 1.50\nTotal: 29.83\n'

    def test_calculate_total_utf8(self):
        cart = Cart(self.input_utf8)
        self.assertEqual(
            cart.calculate_total(), ((Decimal('29.83'), Decimal('1.50'))))

    def test_calculate_total_example1(self):
        cart = Cart(self.input1)
        self.assertEqual(
            cart.calculate_total(), ((Decimal('29.83'), Decimal('1.50'))))

    def test_calculate_total_example2(self):
        cart = Cart(self.input2)
        self.assertEqual(
            cart.calculate_total(), ((Decimal('65.15'), Decimal('7.65'))))

    def test_calculate_total_example3(self):
        cart = Cart(self.input3)
        print cart.calculate_total()
        self.assertEqual(
            cart.calculate_total(), ((Decimal('74.68'), Decimal('6.70'))))

    def test_receipt_example1(self):
        cart = Cart(self.input1)
        self.assertEqual(
            cart.receipt, self.expectation1)

    def test_receipt_example2(self):
        cart = Cart(self.input2)
        self.assertEqual(
            cart.receipt, self.expectation2)

    def test_receipt_example3(self):
        cart = Cart(self.input3)
        self.assertEqual(
            cart.receipt, self.expectation3)

    def test_receipt_utf8(self):
        cart = Cart(self.input_utf8)
        self.assertEqual(
            cart.receipt, self.expectation_utf8)


class TestModuleFunctions(unittest.TestCase):
    # 2 corrections from the example in the README 'book :' -> 'book:' and '1
    # imported box of chocolates: 11.85' -> '1 box of imported chocolates at:
    # 11.85' in the third input
    expectation = u"Output 1:\n1 book: 12.49\n1 music CD: 16.49\n1 chocolate bar: 0.85\nSales Taxes: 1.50\nTotal: 29.83\nOutput 2:\n1 imported box of chocolates: 10.50\n1 imported bottle of perfume: 54.65\nSales Taxes: 7.65\nTotal: 65.15\nOutput 3:\n1 imported bottle of perfume: 32.19\n1 bottle of perfume: 20.89\n1 packet of headache pills: 9.75\n1 box of imported chocolates: 11.85\nSales Taxes: 6.70\nTotal: 74.68\n"
    expectationutf8 = u"Output 1:\n1 book: 12.49\n1 music CD: 16.49\n1 chocolate bar: 0.85\nSales Taxes: 1.50\nTotal: 29.83\nOutput 2:\n1 imported box of chocolates: 10.50\n1 imported bottle of perfume: 54.65\nSales Taxes: 7.65\nTotal: 65.15\nOutput 3:\n1 imported bottle of perfume: 32.19\n1 bottle of perfume: 20.89\n1 päcket of heädache pills: 9.75\n1 box of imported chocolates: 11.85\nSales Taxes: 6.70\nTotal: 74.68\n"
    input_tax_exempt = "1 book at 12.49\n"
    input_imported = "1 imported bottle of perfume at 27.99\n"
    input_malformed = "dgf<sh<dsfzdfg"
    input_negative = "-1 thing at -2.00"

    def test_is_match_input_sunny_day(self):
        self.assertEqual(
            match_input(self.input_tax_exempt), ('1', 'book', 'at ', '12.49'))

    def test_is_match_input_bigger_name(self):
        self.assertEqual(match_input(self.input_imported),
                         ('1', 'imported bottle of perfume', 'at ', '27.99'))

    def test_is_match_input_blank(self):
        with self.assertRaisesRegexp(ValueError, "Input is not well-formed. Items should take the form of a single line containing a quantity, name of the item, the word 'at' then the price"):
            match_input("\t \n")

    def test_is_match_input_none(self):
        with self.assertRaisesRegexp(TypeError, "expected string or buffer"):
            match_input(None)

    def test_is_match_input_malformed(self):
        with self.assertRaisesRegexp(ValueError, "Input is not well-formed. Items should take the form of a single line containing a quantity, name of the item, the word 'at' then the price"):
            match_input(self.input_malformed)

    def test_is_match_input_negative(self):
        self.assertEqual(
            match_input(self.input_negative), ('-1', 'thing', 'at ', '-2.00'))

    def test_is_item_tax_exempt_true(self):
        self.assertTrue(is_item_tax_exempt(self.input_tax_exempt))

    def test_is_item_tax_exempt_false(self):
        self.assertFalse(is_item_tax_exempt(self.input_imported))

    def test_is_item_tax_exempt_empty(self):
        self.assertFalse(is_item_tax_exempt(""))

    def test_is_item_tax_exempt_none(self):
        with self.assertRaisesRegexp(AttributeError, "'NoneType' object has no attribute 'lower'"):
            is_item_tax_exempt(None)

    def test_is_item_imported_false(self):
        self.assertFalse(is_item_imported(self.input_tax_exempt))

    def test_is_item_imported_true(self):
        self.assertTrue(is_item_imported(self.input_imported))

    def test_is_item_imported_empty(self):
        self.assertFalse(is_item_imported(""))

    def test_is_item_imported_None(self):
        with self.assertRaisesRegexp(AttributeError, "'NoneType' object has no attribute 'lower'"):
            is_item_imported(None)

    def test_parse_file_missing(self):
        with self.assertRaisesRegexp(IOError, "No such file or directory: \'docs/inpucxt.txt\'"):
            parse_files(["docs/inpucxt.txt"])

    def test_parse(self):
        self.assertEqual(parse_files(["docs/input.txt"]), self.expectation)

    def test_parse_utf8(self):
        self.assertEqual(
            parse_files(["docs/inpututf8.txt"]), self.expectationutf8)

    def test_parse_multiple_files(self):
        self.assertEqual(parse_files(
            ["docs/input.txt", "docs/inpututf8.txt"]), self.expectation + self.expectationutf8)

    def test_apply_rounding(self):
        self.assertEqual(apply_rounding(Decimal('29.83')), Decimal('29.85'))

    def test_apply_rounding_same(self):
        self.assertEqual(apply_rounding(Decimal('0.05')), Decimal('0.05'))

    def test_apply_rounding_up(self):
        self.assertEqual(apply_rounding(Decimal('29.82')), Decimal('29.85'))

    def test_apply_rounding_up_precision(self):
        self.assertEqual(
            apply_rounding(Decimal('29.8000000000001')), Decimal('29.85'))

    def test_apply_rounding_size_limits(self):
        self.assertEqual(apply_rounding(Decimal('9999999999999999999999999.01')), Decimal(
            '9999999999999999999999999.05'))
