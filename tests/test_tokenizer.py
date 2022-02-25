from calligraphy_scripting import tokenizer

def test_detect_type():
    token = tokenizer.detect_type('=')
    assert token.t_type == 'ASSIGN'
    assert token.t_value == '='

def test_token_str():
    token = tokenizer.Token('ASSIGN', '=')
    assert str(token) == '<ASSIGN:=>'
