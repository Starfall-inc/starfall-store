def format_price(value):
    if value is None or value == 0:
        return "0.00"
    return "{:,.2f}".format(value)
