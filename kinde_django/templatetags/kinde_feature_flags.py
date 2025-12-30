from asgiref.sync import async_to_sync
from django import template

from kinde_sdk.auth import feature_flags

from django import template
from django.template.base import VariableDoesNotExist


register = template.Library()


def flag_is_active(request, flag_name):
    print(f'Checking flag {flag_name}')
    flag = async_to_sync(feature_flags.get_flag)(flag_name)
    print(f'Flag {flag_name} is {flag.value}')
    return flag.value


class KindeFlagNode(template.Node):
    child_nodelists = ('nodelist_true', 'nodelist_false')

    def __init__(self, nodelist_true, nodelist_false, condition, name,
                 compiled_name):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.condition = condition
        self.name = name
        self.compiled_name = compiled_name

    def __repr__(self):
        return f'<KindeFlagNode: {self.name}>'

    def __iter__(self):
        yield from self.nodelist_true
        yield from self.nodelist_false

    def render(self, context):
        try:
            name = self.compiled_name.resolve(context)
        except VariableDoesNotExist:
            name = self.name
        if not name:
            name = self.name
        print(f'Checking flag {name}')
        print('result:', self.condition(context.get('request', None), name))
        if self.condition(context.get('request', None), name):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)

    @classmethod
    def handle_token(cls, parser, token, kind, condition):
        bits = token.split_contents()
        if len(bits) < 2:
            raise template.TemplateSyntaxError(f"{bits[0]!r} tag requires an argument")

        name = bits[1]
        compiled_name = parser.compile_filter(name)

        nodelist_true = parser.parse(('else', f'end{kind}'))
        token = parser.next_token()
        if token.contents == 'else':
            nodelist_false = parser.parse((f'end{kind}',))
            parser.delete_first_token()
        else:
            nodelist_false = template.NodeList()

        return cls(nodelist_true, nodelist_false, condition,
                   name, compiled_name)


@register.tag
def kinde_feature_flag(parser, token):
    return KindeFlagNode.handle_token(parser, token, 'kinde_feature_flag', flag_is_active)

