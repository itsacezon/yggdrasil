#!/usr/bin/python2.7


import xml.etree.ElementTree as ET
import collections as coll
import os


class DecTree:
    @staticmethod
    def build_tree(inp, out, data):
        def ent(attr, data):
            from math import log
            e = [d[attr] for d in data]
            v = coll.Counter(e)
            p = [float(v[x])/len(e) for x in v.keys()]
            return -sum(p*(log(p)/log(2)) for p in p)

        def rem(attr, var, data):
            e = [(d[var], d[attr]) for d in data]
            v = coll.Counter(e)
            t = coll.defaultdict(int)
            for k in v.keys():
                t[k[0]] += v[k]
            # build new dataset
            d = dict((k, [{x: y} for x, y in e if x == k]) for k in t.keys())
            return sum((float(t[k])/len(e))*ent(k, d[k]) for k in t.keys())

        def gain(attr, var, data):
            return ent(attr, data) - rem(attr, var, data)

        def tree():
            return coll.defaultdict(tree)

        def add(t, keys):
            for key in keys:
                t = t[key]

        dectree = tree()  # instant tree! wow!

        def decide(inp, out, data, path=[]):
            gains = dict((i, gain(out, i, data)) for i in inp)
            if sum(gains.values()) <= 0:
                add(dectree, path+[data[0][out]])
            else:
                best = max(gains, key=gains.get)
                path.append(best)
                branches = list(set([d[best] for d in data]))
                for branch in branches:
                    d = [d for d in data if d[best] == branch]
                    decide(inp, out, d, path+[branch])

        decide(inp, out, data)
        dicts = lambda t: dict((k, dicts(t[k])) for k in t)
        return dicts(dectree)

    @staticmethod
    def classify(d, t):
        def get(d, t, mode="key", kv=""):
            for k in t:
                if mode == "key":
                    if t[k] == {}:
                        return k
                    elif d[k]:
                        return get(d, t[k], "val", k)
                else:
                    if d[kv] == k:
                        return get(d, t[k], "key", None)
        return get(d, t)


if __name__ == "__main__":
    inp, out = [], []
    def feed(filename, mode, dectree=None):
        data = []
        f = open(filename, 'r').read().lower()
        for c in ET.fromstring(f):
            if c.tag == "parameter":
                param = {'input': inp, 'output': out}[c.attrib['type']]
                param.append(c.text)
            elif c.tag == "example" and c.attrib['type'] == mode:
                data.append({a.attrib['parameter']: a.text for a in c})

        if mode == "training":
            return DecTree.build_tree(inp, out[0], data)
        elif mode == "testing":
            correct = 0
            for d in data:
                t = d[out[0]]
                del d[out[0]]
                if t == DecTree.classify(d, dectree):
                    correct += 1
            return float(correct)/len(data) * 100

    import argparse
    parser = argparse.ArgumentParser(description="Yggdrasil by Acezon Cay")
    subparsers = parser.add_subparsers(title="Actions")

    train = subparsers.add_parser('train', help="Train data")
    train.add_argument('-f', '--file', type=str, help="Filename of training data", required=True)
    train.set_defaults(subparser='train')

    test = subparsers.add_parser('test', help="Test data")
    test.add_argument('-t', '--tree', type=str, help="Decision tree file", required=True)
    testargs = test.add_mutually_exclusive_group(required=True)
    testargs.add_argument('-q', '--query', nargs='+', help="Use querying")
    testargs.add_argument('-f', '--file', type=str, help="Use file testing (include testing file)")
    test.set_defaults(subparser='test')

    args = vars(parser.parse_args())

    if args['subparser'] == 'train':
        train_file = args['file']
        if not os.path.isfile(train_file):
            train.error(train_file + " does not exist.")
        tree = feed(train_file, "training")

        tree_filename = os.path.splitext(train_file)[0]+".tree"
        with open(tree_filename, "w") as file:
            file.write(str(inp)+"\n")
            file.write(str(tree))
            print "\n", "Saved decision tree file at", tree_filename
    elif args['subparser'] == 'test':
        tree_file = args['tree']
        if not os.path.isfile(tree_file):
            train.error(tree_file + " does not exist.")

        with open(tree_file, "r") as file:
            import ast
            inputs = ast.literal_eval(file.readline())
            dicttree = ast.literal_eval(file.readline())

        if args['query']:
            if not len(inputs) == len(args['query']):
                test.error("Number of query arguments is not equal to the number of input parameters. You entered " + str(len(args['query'])) + " parameter/s when the required is " + str(len(inputs)))
            queries = {}
            for query in args['query']:
                try:
                    param, value = query.split("=")
                except:
                    test.error("Please follow query argument format: param=value")
                if param in inputs:
                    queries[param] = value
                else:
                    test.error("Unknown parameter: " + param)
            result = DecTree.classify(queries, dicttree)
            print "\nResult:", result
        elif args['file']:
            test_file = args['file']
            if not os.path.isfile(test_file):
                test.error(test_file + " does not exist.")
            acc = feed(test_file, "testing", dicttree)
            print "\nAccuracy:", acc, "%"
