"""Public flat configuration contract, schema subset 1.

MIT License

Copyright (c) 2026 HouseNimble plugin-template contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import json
import math
import re

class ConfigurationError(ValueError):pass


def configure(schema,overrides=None):
    def require(condition):
        if not condition:raise ConfigurationError('Unsupported schema or invalid plugin settings')
    require(isinstance(schema,dict) and schema.get('type')=='object' and schema.get('additionalProperties') is False)
    require(set(schema)<={'$schema','title','description','type','additionalProperties','properties','required'})
    properties=schema.get('properties');require(isinstance(properties,dict) and len(properties)<=16)
    require(overrides is None or isinstance(overrides,dict));overrides={} if overrides is None else overrides
    require(set(overrides)<=set(properties))
    required=schema.get('required',[]);require(isinstance(required,list) and all(isinstance(k,str) for k in required) and len(set(required))==len(required) and set(required)<=set(properties))
    output={}
    for key,definition in properties.items():
        require(isinstance(key,str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,31}',key) and isinstance(definition,dict))
        require(set(definition)<={'type','title','description','default','enum','minimum','maximum','minLength','maxLength'})
        kind=definition.get('type');require(kind in ('string','number','integer','boolean') and 'default' in definition)
        if kind in ('number','integer'):
            require(not {'minLength','maxLength'}&set(definition))
            for bound in ('minimum','maximum'):
                if bound in definition:
                    try:finite=type(definition[bound]) in (int,float) and math.isfinite(definition[bound])
                    except OverflowError:finite=False
                    require(finite)
            require(definition.get('minimum',-math.inf)<=definition.get('maximum',math.inf))
        else:require(not {'minimum','maximum'}&set(definition))
        if kind=='string':
            for bound in ('minLength','maxLength'):
                if bound in definition:require(type(definition[bound]) is int and 0<=definition[bound]<=128)
            require(definition.get('minLength',0)<=definition.get('maxLength',128))
        else:require(not {'minLength','maxLength'}&set(definition))
        def valid(value):
            if kind=='boolean':return type(value) is bool
            if kind=='string':
                try:return isinstance(value,str) and '\x00' not in value and len(value.encode('utf-8'))<=128 and definition.get('minLength',0)<=len(value)<=definition.get('maxLength',128)
                except UnicodeError:return False
            try:return type(value) in (int,float) and math.isfinite(value) and (kind!='integer' or value==math.floor(value)) and definition.get('minimum',-math.inf)<=value<=definition.get('maximum',math.inf)
            except OverflowError:return False
        require(valid(definition['default']))
        values=definition.get('enum')
        if 'enum' in definition:require(isinstance(values,list) and 1<=len(values)<=32 and all(valid(v) for v in values) and definition['default'] in values)
        value=overrides[key] if key in overrides else definition['default'];require(valid(value))
        require(values is None or value in values)
        output[key]=value
    require(len(json.dumps(output,ensure_ascii=True,separators=(',',':')).encode())<=768)
    return output
