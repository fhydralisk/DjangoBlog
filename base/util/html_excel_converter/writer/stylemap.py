import xlwt


MAP = {
    'border': {
        'default': 'border: left {}, right {}, top {}, bottom {}'.format(*['thin' for _ in range(4)]),
        '0': 'border: left {}, right {}, top {}, bottom {}'.format(*['no_line' for _ in range(4)]),
        '1': 'border: left {}, right {}, top {}, bottom {}'.format(*['thin' for _ in range(4)]),
    },
    'text-align': {
        'default': 'align: horz general, vert center',
        'center': 'align: horz center, vert center',
    },
    'word-wrap': {
        'normal': None,
        'break-word': 'align: wrap on',
        'word-break': 'align: wrap on',
    }
}


def html_style_to_xls(raw_style_dic):
    css_style_dict = {}
    for style in raw_style_dic.get('style', '').split(';'):
        try:
            k, v = style.split(':')
        except ValueError:
            pass
        else:
            k = k.strip()
            v = v.strip()
            if k and v:
                css_style_dict[k] = v

    xls_style = ''
    xls_style += MAP['border'].get(raw_style_dic.get('border', 1), MAP['border']['default']) + ';'
    xls_style += MAP['text-align'].get(raw_style_dic.get('text-align', 1), MAP['text-align']['default']) + ';'

    for style_key, style_value in css_style_dict.items():
        xls_style_element = MAP.get(style_key, {}).get(style_value, None)
        if xls_style_element:
            xls_style += xls_style_element + ';'

    return xls_style

