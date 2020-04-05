import decimal


def decimal_round(num, digit, rounding=decimal.ROUND_HALF_UP):
    # type: (decimal.Decimal, int, any) -> decimal.Decimal
    if isinstance(num, float):
        return round(num, digit)
    else:
        return num.quantize(decimal.Decimal((0, (0, ), -digit)), rounding=rounding)
