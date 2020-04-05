import decimal


def fake_pn_iterator(start=decimal.Decimal('13600000000')):
    fake_pn = start
    while True:
        yield str(fake_pn)
        fake_pn += decimal.Decimal('1')
