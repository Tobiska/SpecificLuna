import json
import os
 

#read jsn file and write to data
def read_json_file(js_name):
    """ Read json file
        Keyword arguments:
            js_name  - name of json file
            Return dictionary which reads from json file
    """
    json_data = open(js_name)
    data = json.load(json_data)
    json_data.close()
    return data

def write_json_file(out_name, js):
    """Write to json file
        
        Keyword arguments:
            out_name - name of output json file 
            js - dictionary which need to write to json file
    """
    new_js_name = out_name
    new_js = open(new_js_name,'w')
    json.dump(js,new_js, indent=4)
    new_js.close()


def isEmpty(filename):
    st = os.stat(filename)
    if st.st_size == 0:
        return True
    else:
        return False

def write_file(out_name, s, param='w'): 
    f = open(out_name, param)
    f.write(s)
    f.close()
