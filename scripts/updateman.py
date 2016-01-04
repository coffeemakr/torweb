import xml.etree.ElementTree
import json
import os
import re

def tag(name):
    return './/{http://www.w3.org/1999/xhtml}' + name

def div(cls):
    'Z'
    return tag('div') + "[@class='%s']" % cls


def get_option(definition):
    a = definition.find(tag('a'))
    if a is None:
        s = definition.find(tag('strong'))
        return s.text, True
    else:
        name = a.attrib['id']
        return name, False

def get_content(content):
    c = ""
    for p in content.findall('./{http://www.w3.org/1999/xhtml}p'):
        c += xml.etree.ElementTree.tostring(p) + '\n'
    c =  c[len('<html:p xmlns:html="http://www.w3.org/1999/xhtml">'): - len('</html:p>') - 2]
    c = c.replace('\t', '').replace('\n', '').replace('    ', ' ')    
    for tag in ('strong', 'em', 'code', 'br', 'li', 'ul', 'ol'):
        c = c.replace('html:' + tag + '>', tag + '>')
    c = c.replace('<html:br />', '<br/>')
    c = re.sub(r'</? ?html:[^>]*>', '', c)
    return c

def main():
    "run"
    result = {}
    root = xml.etree.ElementTree.parse('/usr/share/doc/tor/tor.html').getroot()
    print root
    for section in root.findall(div('sect1')):
        head = section.find('.//{http://www.w3.org/1999/xhtml}h2')
        if not head.text.endswith('OPTIONS') or \
           head.text == 'COMMAND-LINE OPTIONS':
            continue
        option_category = head.text[:-8].lower()
        print option_category
        for dlist in section.findall(div('dlist')):
            definitions = dlist.findall(tag('dt'))
            content = dlist.findall(tag('dd'))
            
            d_i = 0
            c_i = 0
            
            while d_i < len(definitions):
                d = definitions[d_i]
                c = content[c_i]
                option = {}

                name, second = get_option(d)
                if second:
                    print "ignoring second definition: "  + name
                    d_i += 1
                    continue
                h = get_content(c)
                result[name] = ({'name': name, 'help': h, 'category': option_category})

                d_i += 1
                c_i += 1
                last_option = option

    basedir = os.path.split(__file__)[0]
    with open(os.path.join(basedir, '../app/js/confighelp.json'), 'w') as f:
        json.dump(result, f, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    main()