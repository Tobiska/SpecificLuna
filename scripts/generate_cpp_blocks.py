import json
import sys

from scripts.common import to_string, to_String

C_TYPES={
    'int': 'int',
    'real': 'double',
    'string': 'const char *',
    'value': 'const InputDF &',
    'name': 'OutputDF &'
}


def get_path_id(path, id2path, path2id, SRC):
    if path in path2id:
        return path2id[path]
    else:
        id=len(path2id)
        path2id[path]=id
        id2path[id]=path
        return id


def generate_cpp_blocks(ja_in_path, headers_in_path, ja_ti_path, b_in_path,
                        ja_out_path, b_out_path, b_ti_path):
    ja = json.loads(open(ja_in_path).read())
    try:
        hja = json.loads(open(headers_in_path).read())
    except IOError:
        hja = []
    blocks = json.loads(open(b_in_path).read())

    path2id = {}
    id2path = {}
    SRC = {}
    Cpp = []

    for C in to_String(SRC, path2id, id2path, '#include "ucenv.h"\n\n'):
        Cpp.append(C)

    for header in hja:
        if header[0] == 'head':
            block_id = header[1]
            for C in blocks['text'][block_id]:
                Cpp.append(C)
        else:
            raise NotImplementedError(header[0], header)

    for name, sub in ja.items():
        if sub['type'] == 'foreign_cpp':
            block_id = sub['block_id']

            # Generate signature
            sig = 'extern "C" void __foreign_block_%d(' % block_id

            sig += ', '.join(['%s %s' % (C_TYPES[arg['type']], arg['id']) \
                              for arg in sub['args']])

            sig += ')\n'

            for C in to_String(SRC, path2id, id2path, sig):
                Cpp.append(C)

            # Append block

            for C in blocks['text'][block_id]:
                path = blocks['paths'][str(C[0])]
                C[0] = get_path_id(path, id2path, path2id, SRC)

                Cpp.append(C)

            sub['type'] = 'extern'
            sub['foreign_type'] = 'C++'
            sub['code'] = '__foreign_block_%d' % block_id
            del sub['block_id']

    open(b_out_path, 'w').write(to_string(Cpp))
    open(b_ti_path, 'w').write(json.dumps({
        "paths": id2path,
        "text": Cpp
    }))
    open(ja_out_path, 'w').write(json.dumps(ja))


if __name__ == '__main__':
    generate_cpp_blocks(
        sys.argv[0],
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6]
    )