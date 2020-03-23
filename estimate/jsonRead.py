import json

def jsonRead(fileName):
    jsonFolder = './example/seg_result/json/'
    with open(jsonFolder+fileName[:-3]+'json', 'r') as f:
        load_dict = json.load(f)

    return load_dict
