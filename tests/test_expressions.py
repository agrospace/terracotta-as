import pytest

from textwrap import dedent

import numpy as np


OPERANDS = {
    'v1': np.random.rand(5),
    'v2': 2 * np.random.rand(5)
}


VALID_EXPR = (
    # identity
    ('v1', OPERANDS['v1']),

    # multiline
    (
        dedent('''
        (
            v1 +
            v1
        )
        '''),
        2 * OPERANDS['v1']
    ),

    # abs
    ('abs(v1)', np.abs(OPERANDS['v1'])),

    # sqrt and *
    ('sqrt(v1 * v1)', OPERANDS['v1']),

    # sqrt and **
    ('sqrt(v1 ** 2)', OPERANDS['v1']),

    # /
    ('v1 / v1', np.ones_like(OPERANDS['v1'])),

    # %
    ('v1 % v1', np.zeros_like(OPERANDS['v1'])),

    # simple index calculation
    (
        '(v2 - v1) / (v2 + v1)',
        (OPERANDS['v2'] - OPERANDS['v1']) / (OPERANDS['v2'] + OPERANDS['v1'])
    ),

    # conditionals
    (
        'where(v2 > v1, 100, 0)', np.where(OPERANDS['v2'] > OPERANDS['v1'], 100, 0)
    ),

    # comparisons
    ('v1 == v2', OPERANDS['v1'] == OPERANDS['v2']),
    ('v1 != v2', OPERANDS['v1'] != OPERANDS['v2']),
    ('v1 > v2', OPERANDS['v1'] > OPERANDS['v2']),
    ('v1 < v2', OPERANDS['v1'] < OPERANDS['v2']),
    ('v1 >= v2', OPERANDS['v1'] >= OPERANDS['v2']),
    ('v1 <= v2', OPERANDS['v1'] <= OPERANDS['v2']),
    ('(v1 < 0.5) & (v2 > 0.5)', (OPERANDS['v1'] < 0.5) & (OPERANDS['v2'] > 0.5)),
    ('(v1 < 0.5) | (v2 > 0.5)', (OPERANDS['v1'] < 0.5) | (OPERANDS['v2'] > 0.5)),
    ('~(v1 < 0.5) & (v2 > 0.5)', ~(OPERANDS['v1'] < 0.5) & (OPERANDS['v2'] > 0.5)),

    # maximum
    (
        'maximum(v1, v2)', np.maximum(OPERANDS['v1'], OPERANDS['v2'])
    ),

    # minimum
    (
        'minimum(v1, v2)', np.minimum(OPERANDS['v1'], OPERANDS['v2'])
    ),

    # sin / arcsin
    (
        'arcsin(sin(v1))', np.arcsin(np.sin(OPERANDS['v1']))
    ),

    # trigonometry
    (
        'sin(pi * v1)', np.sin(np.pi * OPERANDS['v1'])
    ),

    # long expression
    (
        '+'.join(['v1'] * 1000), sum(OPERANDS['v1'] for _ in range(1000))
    )
)


INVALID_EXPR = (
    # haxx
    ('__builtins__["dir"]', 'not allowed in expressions'),

    # uses list
    ('[0] * 1000000000', 'not allowed in expressions'),

    # uses dict
    ('{}', 'not allowed in expressions'),

    # uses string
    ('"general kenobi!"', 'not allowed in expressions'),

    # if construct
    ('if True: v1', 'is not a valid expression'),

    # inline comparison
    ('v1 if True else 0', 'not allowed in expressions'),

    # and
    ('v1 and v2', 'not allowed in expressions'),

    # does not return an array
    ('0', 'does not return an array'),

    # more than one expression
    ('v1; v1', 'is not a valid expression'),

    # dunder method
    ('__name__', 'unrecognized name \'__name__\''),

    # builtins
    ('dir(v1)', 'unrecognized name \'dir\''),

    # method call
    ('v1.mean()', 'not allowed in expressions'),

    # attribute access
    ('v1.size', 'not allowed in expressions'),

    # unknown operand
    ('v100', 'unrecognized name \'v100\''),

    # not a valid expression
    ('k = v1', 'is not a valid expression'),

    # internal numpy error (mismatching types)
    ('v1 & v2', 'unexpected error'),

    # code injection (serious haxx)
    (
        dedent('''
               (lambda fc=(
                   lambda n: [
                       c for c in
                           ().__class__.__bases__[0].__subclasses__()
                           if c.__name__ == n
                       ][0]
                   ):
                   fc("function")(
                       fc("code")(
                           0,0,0,0,"KABOOM",(),(),(),"","",0,""
                       ),{}
                   )()
               )()
               '''),
        'not allowed in expressions'
    )

)


@pytest.mark.parametrize('case', VALID_EXPR)
def test_valid_expression(case):
    from terracotta.expressions import evaluate_expression

    expr, result = case

    np.testing.assert_array_equal(
        evaluate_expression(expr, OPERANDS),
        result
    )


@pytest.mark.parametrize('case', INVALID_EXPR)
def test_invalid_expression(case):
    from terracotta.expressions import evaluate_expression

    expr, exc_msg = case

    with pytest.raises(ValueError) as raised_exc:
        evaluate_expression(expr, OPERANDS)

    assert exc_msg in str(raised_exc.value)
