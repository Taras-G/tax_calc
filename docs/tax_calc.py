#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module  is used to calculate the taxes for shopping cart of goods.

The Cart class consumes a string or unicode representation of a shopping list, 
calculatures applicable sales taxes on the items, then formats a receipt of the 
purchases

It internally represents the goods as instances of the Item class

command-line use of this module will take a list of file descriptors as 
arguments and return a formated recipt for each input. The file 
descriptors should point to ASCII or UTF-8 encoded string representations
of shopping carts of the format below:

Input 1:
1 book at 12.49
1 music CD at 14.99
1 chocolate bar at 0.85

Input 2:
1 imported box of chocolates at 10.00
1 imported bottle of perfume at 47.50

Input 3:
1 imported bottle of perfume at 27.99
1 bottle of perfume at 18.99
1 packet of headache pills at 9.75
1 box of imported chocolates at 11.25

Empty lines delimit seperate carts,
lines with begining with the word "input" are ignored. 
"""

from decimal import Decimal, ROUND_CEILING
import codecs

# questionable, but best given the input
_TAX_EXEMPT_GOODS = ["book", "pill", "chocolate"]


class Cart(object):

    """Represents a shopping cart generated from a list of purchased items,
    and their prices. Used to print a receipt that includes applicable taxes.
    """

    def __init__(self, shopping_cart):
        self.receipt = ""
        self.items = []
        for item in shopping_cart.split(u'\n'):
            if item.strip() is not u"":
                formated_item = Item(item)
                self.items.append(formated_item)
                self.receipt += unicode(formated_item) + u"\n"
        total, sales_tax = self.calculate_total()
        self.receipt += u"Sales Taxes: %s\n" % sales_tax
        self.receipt += u"Total: %s\n" % total

    def calculate_total(self):
        """Calculates total sales tax and final price of a cart of items
        """
        total = 0
        sales_tax = 0
        for item in self.items:
            total += item.get_item_price()
            sales_tax += item.get_tax_amount()
        return total, sales_tax

    def __str__(self):
        return self.receipt


class Item:

    """Representation of one item type on a shopping cart, calculates taxes for
    that item based on its quantity, price and taxt status (imported, exempt)
    """

    def __init__(self, item):
        if not item or not item.strip():
            raise ValueError('Basket must contain valid purchases')
        tokens = item.split()
        # first and last are quantity and price respectively
        self.quantity = Decimal(tokens[0])
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        self.unit_price = Decimal(tokens[-1])
        if self.unit_price < 0:
            raise ValueError("Price of items cannot be negative")
        self.imported = is_item_imported(item)
        self.tax_exempt = is_item_tax_exempt(item)
        #output expects colon and adjusted price
        self.string_rep = item.replace(" at " + tokens[-1], ": " + str(self.get_item_price()))

    def get_tax_rate(self):
        """Calculates amount of taxes charged given what is known about 
        this item being tax exempt or imported
        """
        taxes = Decimal('0')
        if not self.tax_exempt:
            taxes = Decimal('0.1')
        if self.imported:
            taxes += Decimal('0.05')
        return taxes

    def get_tax_amount(self):
        untaxed_cost = (self.quantity * self.unit_price).quantize(Decimal('0.01'))
        sales_tax = (untaxed_cost * self.get_tax_rate()).quantize(Decimal('0.01'))
        return apply_rounding(sales_tax)

    def get_item_price(self):
        untaxed_cost = (self.quantity * self.unit_price).quantize(Decimal('0.01'))
        return untaxed_cost + self.get_tax_amount()

    def __str__(self):
        return self.string_rep


def is_item_imported(item):
    """returns true if the good looks like a tax exempt product,
    which amounts searching for the word 'imported' in its name
    """
    item = item.lower()
    if "imported" in item:
        return True
    else:
        return False


def is_item_tax_exempt(item):
    """returns true if the good looks like a tax exempt product,
    which amounts searching for similar keywords within the name
    """
    item = item.lower()
    for untaxable in _TAX_EXEMPT_GOODS:
        if untaxable in item:
            return True
    return False

def apply_rounding(number, precision=Decimal('0.05')):
    """Applies rounding according to:
    The rounding rules for sales tax are that for a tax rate of n%, 
    a shelf price of p contains (np/100 rounded up to the nearest 0.05) 
    amount of sales tax."""
    # catchall in case a float sneaks by
    number = Decimal(number)
    precision = Decimal(precision)
    rounding = (number / precision).quantize(Decimal('1'),
                                             rounding=ROUND_CEILING)
    return (rounding * precision).quantize(Decimal('0.01'))



def parse_files(filenames):
    """
    function that iterates over a list of filenames, treating each as 
    cart(s) and printing receipts
    """
    stdout = ""
    for filename in filenames:
        print "Receipts from " + filename
        with codecs.open(filename, "r", "utf-8") as file_in:
            carts = [""]
            i = 0
            within_cart = False
            # iterate over lines, ignore blank lines and input delimiters
            for line in file_in:
                if line.lower().startswith(u'input') or line.strip() is u"":
                    if within_cart:
                        i += 1
                        carts.append(u"")
                    within_cart = False
                else:
                    within_cart = True
                    carts[i] += line
            # shopping lists seperated, construct receipts
            j = 1
            for cart in carts:
                if cart is not "":
                    stdout += u"Output %s:\n" % j
                    stdout += unicode(Cart(cart))
                    j += 1
    return stdout

# CLI use
if __name__ == "__main__":
    import sys
    # ignoring first arg as it's this file's name
    print parse_files(sys.argv[1:])
