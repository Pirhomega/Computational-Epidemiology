import json

def load_params(infile):
    with open(infile,'r') as f:
        data = f.read()
        param = json.loads(data)
    return param