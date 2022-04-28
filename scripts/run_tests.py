#!/usr/bin/env python3

import sys, os, subprocess, re, time

_prog=os.path.split(sys.argv[0])[1]
HELP_MESSAGE=sys.argv[0] + '''

NAME
	''' + _prog + ''' - LuNA tests runner

SYNOPSIS
	''' + _prog + ''' [--no-color] [--first-fail]
	''' + _prog + ''' --help

DESCRIPTION
	Runs tests. Tests are looked up from current directory. Each test
	has 'conf' file, which specifies how the test must be conducted
	and how to validate its execution. 'conf' format is described
	below

OPTIONS
	--no-color
	    Disable colors in output.
	
	--first-fail
	    Stop testing after first failed test.

FILES
	'conf' file is a test specification file, which follows common
	format conventions:
	
	Comments and empty lines
	    *) Line is ignored if it starts with '#' (leading whitespaces are
	       allowed).
	    *) Empty lines are ignored.
	    *) No comments in other lines are allowed.
	
	Flags
	    Single key on a line defines a flag.
	
	Parameters
	    Line of form 'key=value' defines a parameter with a value.
	
	Supported flags and parameters:
	    RUN=<line>
	        Specify a command to run (mandatory)

	    RETCODE=<number>
	        Specify which return code is expected (mandatory)
	    
	    STDOUT=<path>
	    STDERR=<path>
	        Check exact match of command stdout/stderr with given file
	        
	    STDOUT_EMPTY
	    STDERR_EMPTY
	        Check that command produced no stdout/stderr
	        
	    STDOUT_MATCH=<regex>
	    STDERR_MATCH=<regex>
	        Check that command's stdout/stderr contains line, that
	        matches the regular expression

	    CLEAN=<file1> <file2>
	        Clean files after test 

	    CHECK=<command>
	        Ensure shell command returns no error


'''

def parse_conf(path):
	conf={}
	for ln in open(path).read().split('\n'):
		if not ln.strip() or ln.strip().startswith('#'):
			continue
		if '=' in ln:
			key, val=ln.split('=', 1)
			val=val.strip()
		else:
			key, val=ln, None
		key=key.strip()
		if key in conf:
			assert key in ['CHECK']
			if type(conf[key])!=list:
				x=conf[key]
				conf[key]=[x]
			conf[key].append(val)
		else:
			conf[key]=val
		
	assert 'RETCODE' in conf
	assert 'RUN' in conf
	return conf

def run_test(path):
	sys.stdout.write('    TEST %s' % path)
	sys.stdout.flush()

	orig_filelist=os.listdir(path)

	conf=parse_conf(os.path.join(path, 'conf'))
	
	if 'CAPTION' in conf:
		sys.stdout.write(' %s' % conf['CAPTION'])
		sys.stdout.flush()

	p=subprocess.Popen(conf['RUN'], shell=True, stdout=subprocess.PIPE,
		stderr=subprocess.PIPE, cwd=path)
	out, err=p.communicate()
	out=out.decode('utf-8')
	err=err.decode('utf-8')

	errors=[]

	for k in conf:
		# Connected to: help message
		if k not in ['RUN', 'RETCODE', 'STDOUT', 'STDERR', 'STDOUT_EMPTY',
				'STDERR_EMPTY', 'STDERR_MATCH', 'STDOUT_MATCH', 'CLEAN',
				'CHECK']:
			raise NotImplementedError(k, conf[k])


	if conf['RETCODE']!=str(p.returncode):
		errors.append('RETCODE error: got: %d, expected: %s' % (
			p.returncode, conf['RETCODE']))
	if 'STDOUT' in conf:
		expected=open(os.path.join(path, conf['STDOUT'])).read()
		if expected!=out:
			errors.append('STDOUT error: got:\n%s\nexpected:\n%s' % (
				out, expected))
	
	if 'STDERR' in conf:
		expected=open(os.path.join(path, conf['STDERR'])).read()
		if expected!=err:
			errors.append('STDERR error: got:\n%s\nexpected:\n%s' % (
				err, expected))

	if 'STDOUT_EMPTY' in conf:
		if out:
			errors.append('STDOUT_EMPTY error: got:\n%s' % out)
	
	if 'STDERR_EMPTY' in conf:
		if err:
			errors.append('STDERR_EMPTY error: got:\n%s' % err)
	
	if 'STDOUT_MATCH' in conf:
		matched=False
		for ln in out.split('\n'):
			if re.search(conf['STDOUT_MATCH'], ln):
				matched=True
		if not matched:
			errors.append('STDOUT_MATCH error: expected: "%s" got:\n%s' % \
				(conf['STDOUT_MATCH'], out))

	if 'STDERR_MATCH' in conf:
		matched=False
		for ln in err.split('\n'):
			if re.search(conf['STDERR_MATCH'], ln):
				matched=True
		if not matched:
			errors.append('STDERR_MATCH error: expected: "%s" got:\n%s' % \
				(conf['STDERR_MATCH'], err))
	
	if 'CHECK' in conf:
		if type(conf['CHECK']) in [str, str]:
			conf['CHECK']=[conf['CHECK']]
		for check in conf['CHECK']:
			p=subprocess.Popen(check, shell=True,
				stdout=subprocess.PIPE, stderr=subprocess.PIPE,
				cwd=path)
			out, err=p.communicate()
			p.wait()
			if p.returncode!=0:
				errors.append(('CHECK error: non-zero retcode: %d; ' \
					+ 'output:\n%s\nerror:\n%s') % (p.returncode, out, err))

	if 'CLEAN' in conf:
		for f in conf['CLEAN'].split(' '):
			try:
				os.remove(os.path.join(path, f))
			except OSError as x:
				errors.append('CLEAN error: %s: %s' % (f, x.args[1]))

	new_filelist=os.listdir(path)
	if new_filelist!=orig_filelist:
		for f in [f for f in new_filelist if f not in orig_filelist]:
			errors.append(
				'FILES error: unexpected file appeared: %s. Removing.' % f)
			os.remove(os.path.join(path, f))
		disappeared=[f for f in orig_filelist if f not in new_filelist]
		if disappeared:
			raise Exception('Test file(s) disappeared', disappeared)
	
	if not errors:
		if '--no-color' in sys.argv[1:]:
			sys.stdout.write('\rOK  \n')
		else:
			sys.stdout.write('\r\033[1;32mOK\033[0m  \n')
		sys.stdout.flush()
		return True
	else:
		if '--no-color' in sys.argv[1:]:
			sys.stdout.write('\rERR \n')
		else:
			sys.stdout.write('\r\033[1;31mERR\033[0m \n')
		sys.stdout.write('%s\n' % '\n'.join(errors))
		sys.stdout.flush()
		if '--first-fail' in sys.argv[1:]:
			sys.stdout.write('ABORT\n')
			sys.exit(1)
		return False

def run_test_tree(path):
	if os.path.exists(os.path.join(path, 'conf')):
		return (1, 0) if run_test(path) else (0, 1)

	tests=[x for x in os.listdir(path) if os.path.isdir(
		os.path.join(path, x))]
	passed=0
	failed=0
	for t in sorted(tests):
		p, f=run_test_tree(os.path.join(path, t))
		passed+=p
		failed+=f
	return passed, failed

if __name__=='__main__':
	if '--help' in sys.argv:
		print(HELP_MESSAGE)
		sys.exit(0)
	
	for f in [f for f in sys.argv[1:] if f.startswith('--')]:
		if f not in ['--help', '--first-fail']:
			raise Exception('invalid key', f)
	
	tests=[x for x in sys.argv[1:] if not x.startswith('--')]

	if not tests:
		tests=[os.path.abspath(x)
			for x in os.listdir('.') if os.path.isdir(x)]

	passed=0
	failed=0
	for t in sorted(tests):
		p, f=run_test_tree(t)
		passed+=p
		failed+=f
	print("TESTING DONE. passed: %d failed: %d" % (passed, failed))
	
	if passed>0 and failed==0:
		sys.exit(0)
	else:
		sys.exit(1)
