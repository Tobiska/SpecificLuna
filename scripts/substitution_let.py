import sys
import argparse
import work_json_file as wjf
from pprint import pprint
import copy


def createParse ():
    parser = argparse.ArgumentParser(prog ='set_let2', description = '''The program parsed input json
        file and substitution value of let. Result is saved into ouput json file or rewrite input json file. In order to write or read
        json file  program uses work_json_file module''',
        epilog = '''(C) August, 2014 ''')
    parser.add_argument ('input_file', help='name of json file is processed', metavar = 'INPUT_JSON_FILE')
    parser.add_argument ('--out', help = 'name of output file', metavar = 'OUTPUT_JSON_FILE')
    return parser 

class set_let:
    def __init__(self):
        self.dic = {}
        self.new_dic = {}
        self.it = 0
        self.key = ''
    
    def parsed_dictionary(self, input_file, output_file = None):
        self.dic = wjf.read_json_file(input_file)
        for p in list(self.dic.keys()):
                self.new_dic[p] = copy.deepcopy(self.dic[p])
                if self.dic[p]['type'] == 'struct':
                        self.key = p
                        new_body = []
                        for it in range(0, len(self.dic[p]['body'])):
                                new_body.extend( self.parsed_complex_body(self.dic[p], self.dic[p]['body'][it], it))

                                self.new_dic[p]['body'] = new_body
                
        if output_file != None:
                wjf.write_json_file(output_file, self.new_dic)
        else:
                wjf.write_json_file(input_file, self.new_dic)
    
    def parsed_complex_body(self, dic, data, ix):
        if data['type'] == 'let':
                let = copy.deepcopy(data)
                ins = self.parsed_let(dic, let)
                #print let
                return ins
                        
        elif data['type'] != 'dfs' and data['type'] != 'exec':
                new_body = []
                for j in range(0, len(data['body'])):
                    new_body.extend(self.parsed_complex_body(data, data['body'][j], j))
                data['body'] = new_body
                return [data]
        else:
            return [data]
    
    def parsed_let(self, dic, data):

        if data['body'][0]['type'] == 'dfs' and len(data['body'][0]['names']) != 0:
            level = 0
            r = {}
            for i in range(0, len(data['params'])):
                dm = {'type':'for','first': data['params'][i]['value'],'last':data['params'][i]['value'], 'var': data['params'][i]['name'], 'where': {'type':'luna'}, 'body': []}
                #print 'Add '  + str(dm) + '\nsize ' + str(len(dm))
                if len(r) == 0:
                    #print 'I tut'
                    r = dm
                    level += 1
                else:
                    cur = r
                    for j in range(1,level):
                        #print "Before " +  str(cur)
                        cur = cur['body'][0]
                        #print "After" +  str(cur)
                    cur['body'].append(dm)
                    level +=1
                    #print 'Result ' +str(r)
            flag = 1
            cur = r
            while(flag):
                if len(cur['body']) == 0:
                    cur['body'].extend(data['body'])
                    flag = 0
                else:
                    cur = cur['body'][0]
            #print 'All Result ' +str(r)
            d = [r]
        else:
            for i in range(0, len(data['params'])):
                set_var(data['body'], data['params'][i]['name'], data['params'][i]['value'])
                for j in range(i+1, len(data['params'])):
                        set_var_arg(data['params'][j]['value'], data['params'][i]['name'], data['params'][i]['value'])

            new_body = []
            for k in range(0, len(data['body'])):
                new_body.extend(self.parsed_complex_body(data, data['body'][k], k))
        
            if new_body[0]['type'] == 'dfs':
                d = new_body[1:]
            else:
                d = new_body
        return d
                        
                        #new_dfs = []
                        #for i in range(0, len(new_body[0]['names'])):
                        #    new_dfs += ['let'+str(self.it)]
                        #    set_var(new_body[1:], new_body[0]['names'][i], {'type':'id','ref':['let'+str(self.it)]})
                        #    self.it +=1
            
                        #if self.new_dic[self.key]['body'][0]['type'] == 'dfs':
                        #    self.new_dic[self.key]['body'][0]['names'].extend(new_dfs) 
                        #else:
                        #    print self.key
                        #    print self.new_dic[self.key]['body'][0]['type']
                        #    
                        #d = new_body[1:]
                        
                        #print 'Error: locally declared df is not supported in let-block\n'
                        #sys.exit(1)

        return d

def set_var_arg(arg, var, val, flag=False):
        if arg['type'] == 'id':
                if arg['ref'][0] == var:
                        if len(arg['ref']) == 1:
                                return val
                        else:
                                if val['type'] == 'id':
                                        ins = val['ref']+[set_var_arg(x, var, val) for x in arg['ref'][1:]]
                                        arg['ref'] = ins
                                        return arg
                                else:
                                        print('Error: substitution of {0} instead of id is not allowed\n'.format(val['type']))
                                        sys.exit(1)        
                else:
                        ins = [arg['ref'][0]] + [set_var_arg(x, var, val) for x in arg['ref'][1:]]
                        arg['ref'] = ins 
                        return arg
                        
        elif arg['type'] == '-' or arg['type'] == '+' or arg['type'] == '*' or arg['type'] == '/' or  arg['type'] == '%' or arg['type'] == '>' or arg['type'] == '>=' or arg['type'] == '<' or arg['type'] == '<=' or arg['type'] == '==' or arg['type'] == '!=' or arg['type'] == '&&' or arg['type'] == '||' or arg['type'] == '?:':
                ins = [set_var_arg(x, var, val) for x in arg['operands']]
                arg['operands'] = ins
                return arg
        elif arg['type'] == 'icast' or arg['type'] == 'rcast' or arg['type'] == 'scast':
                arg['expr'] = set_var_arg(arg['expr'], var, val)
                return arg
        else:
                return arg
        

def set_var_exec(data, var, val):

        for i in range(1, len(data['id'])):
            data['id'][i] = set_var_arg(data['id'][i],var,val)

        ins = []
        for i in range(0, len(data['args'])):
                ins.append(set_var_arg(data['args'][i], var,val))
        data['args'] = ins
        if data['rules'] != []:
            inp = []
            for j in range(0, len(data['rules'][0]['dfs'])):
                inp.append(set_var_arg(data['rules'][0]['dfs'][j], var,val))
            data['rules'][0]['dfs'] = inp

def set_var_for(data, var, val):
        data['first'] = set_var_arg(data['first'], var, val)
        data['last'] = set_var_arg(data['last'], var, val)
        if 'where' in data:
                if data['where']['type'] != 'luna':
                        data['where']['size'] = set_var_arg(data['where']['size'], var, val)
                        data['where']['count'] = set_var_arg(data['where']['count'], var, val)
        for j in range(0, len(data['body'])):
                set_var_complex_body(data['body'][j], var, val)
                

def set_var_while(data, var, val):
        data['start'] = set_var_arg(data['start'], var, val)
        data['cond'] = set_var_arg(data['cond'], var, val)
        data['wout'] = set_var_arg(data['wout'], var, val)
        if 'where' in data:
                if data['where']['type'] != 'luna':
                        data['where']['size'] = set_var_arg(data['where']['size'], var, val)
                        data['where']['count'] = set_var_arg(data['where']['count'], var, val)
                        
        for j in range(0, len(data['body'])):
                set_var_complex_body(data['body'][j], var, val)

def set_var_if(data, var, val):
        """ Find const expression in if-discription
                data - if-discription
        """
        data['cond'] = set_var_arg(data['cond'], var, val)
        for j in range(0, len(data['body'])):
                set_var_complex_body(data['body'][j], var, val)


def set_var_let(data, var, val):
        
        for i in range(0, len(data['params'])):
                #print " Before {0}  var {1} value {2}\n".format(data['params'][i]['value'], var, val)
                set_var_arg(data['params'][i]['value'], var, val, True)
                #print " After {0}  var {1} value {2}\n".format(data['params'][i]['value'], var, val)
        for j in range(0, len(data['body'])):
                set_var_complex_body(data['body'][j], var, val)
        

def set_var_complex_body(data, var, val):
        if data['type'] == 'exec':
                set_var_exec(data, var,val)
        elif data['type'] == 'for':
                set_var_for(data, var, val)
        elif data['type'] == 'while':
                set_var_while(data, var, val)
        elif data['type'] == 'if':
                set_var_if(data, var, val)
        elif data['type'] == 'let':
                set_var_let(data, var, val)
                

def set_var(data, var, val):
        #print " Var name {0} value {1}".format(var,val)
        for j in range(0, len(data)):
                set_var_complex_body(data[j],var, val)
                #print data[j]['type']


if __name__ == '__main__':
    parser = createParse()
    namespace = parser.parse_args()
    
    let_a = set_let()
    if namespace.out:
            let_a.parsed_dictionary(namespace.input_file, namespace.out)
    else:
        let_a.parsed_dictionary(namespace.input_file)
