#!/usr/bin/env python3

import json

def R(*objs):
	raise Exception(', '.join([json.dumps(obj, indent=4) for obj in objs]))

def quote(s):
	res=''
	for c in s:
		if c=='"':
			res+='\\"'
		elif c=='\n':
			res+='\\n'
		elif c=='\t':
			res+='\\t'
#		elif c=='%':
#			res+='%%'
		elif 32<=ord(c)<128:
			res+=c
		else:
			R(s, c)
	return res

def repr_ref(x):
	return x[0]+''.join(['[%s]' % repr_expr(idx) for idx in x[1:]])

def repr_expr(x):
	if x['type']=='id':
		return repr_ref(x['ref'])
	elif x['type']=='iconst':
		return '%s' % x['value']
	elif x['type']=='rconst':
		return '%lf' % x['value']
	elif x['type']=='sconst':
		return '"%s"' % quote(x['value'])
	elif x['type']=='icast':
		return 'int(%s)' % repr_expr(x['expr'])
	elif x['type']=='rcast':
		return 'real(%s)' % repr_expr(x['expr'])
	elif x['type'] in '+-*/%':
		return x['type'].join(['(%s)' % repr_expr(op) \
			for op in x['operands']])
	elif x['type'] in ['<', '<=', '==', '!=', '>=', '>', '&&', '||']:
		assert len(x['operands'])==2
		return x['type'].join(['(%s)' % repr_expr(op) \
			for op in x['operands']])
	elif x['type']=='?:':
		assert len(x['operands'])==3
		return '(%s? %s: %s)' % (
			repr_expr(x['operands'][0]),
			repr_expr(x['operands'][1]),
			repr_expr(x['operands'][2])
		)
	else:
		R(x, x['type'])

def repr_exec(ja):
	res='cf %s: %s(%s);' % (
		repr_ref(ja['id']),
		ja['code'],
		', '.join([repr_expr(x) for x in ja['args']])
	)
	if 'line' in ja:
		res+=' @ line:%d' % ja['line']
	return res

def repr_bi(ja):
	if ja['type']=='exec':
		return repr_exec(ja)
	elif ja['type']=='for':
		return 'for %s=%s..%s;' % (ja['var'],
			repr_expr(ja['first']),
			repr_expr(ja['last'])
		)
	elif ja['type']=='while':
		return 'while %s, %s=%s..out %s;' % (
			repr_expr(ja['cond']),
			ja['var'],
			repr_expr(ja['start']),
			repr_ref(ja['wout']['ref'])
		)
	elif ja['type']=='if':
		return 'if %s' % repr_expr(ja['cond'])
	R(ja, ja['type'])

def repr_rule(ja):
	if ja['ruletype']=='assign':
		return '%s %s=%s' % (ja['property'], repr_ref(ja['id']),
			repr_expr(ja['val']))
	elif ja['ruletype']=='enum':
		return '%s %s' % (ja['property'],
			', '.join([repr_ref(ref) for ref in ja['items']]))
	else:
		R(ja)

def repr_for(ja):
	return 'for %s = %s .. %s' % (
		ja['var'],
		repr_expr(ja['first']),
		repr_expr(ja['last'])
	)

def repr_while(ja):
	return 'while %s, %s = %s .. out %s' % (
		repr_expr(ja['cond']),
		ja['var'],
		repr_expr(ja['start']),
		repr_ref(ja['wout']['ref'])
	)

def repr_if(ja):
	return 'if %s' % (repr_expr(ja['cond']))

def repr_struct(ja):
	assert ja['type']=='struct'
	return 'sub %s(%s)' % (ja['name'],
		', '.join(['%s %s' % (x['type'], x['id']) \
			for x in ja['args']]))

def repr_extern(ja):
	assert ja['type']=='extern'
	if 'foreign_type' in ja:
		return 'C++ sub %s(%s)' % (ja['name'],
		', '.join(['%s %s' % (x['type'], x['id']) \
			for x in ja['args']]))
	else:
		return 'import %s(%s) as %s' % (ja['code'],
		', '.join(['%s' % x['type'] \
			for x in ja['args']]), ja['name'])

def repr_ja(ja):
	if ja['type']=='struct':
		return repr_struct(ja)
	elif ja['type']=='exec':
		return repr_exec(ja)
	elif ja['type']=='for':
		return repr_for(ja)
	elif ja['type']=='while':
		return repr_while(ja)
	elif ja['type']=='if':
		return repr_if(ja)
	elif ja['type']=='extern':
		return repr_extern(ja)
	R(ja['type'])

