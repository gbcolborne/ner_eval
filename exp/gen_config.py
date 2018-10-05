import sys, os, argparse, re

doc = """Given the path of a config file, and an optional,
comma-separated list of <key>=<value> pairs, generate a new config
file, using the default values in the original config for any missing
keys, and write to stdout. This script works with Stanford NER and
NeuroNER. For each key provided, it simply looks for lines starting
with this key, and replaces this line (or these lines) with the
<key>=<value> string provided. It does not complain if no lines were
matched or if more than one line matches."""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=doc)
    msg = "comma-separated list of <key>=<value> pairs to replace in template"
    parser.add_argument("-r", "--replace", help=msg)
    parser.add_argument("template", help="path of config file used as template")    
    parser.add_argument("output", help="path of output file")
    args = parser.parse_args()
    args.template = os.path.abspath(args.template)
    args.output = os.path.abspath(args.output)
    
    # Load config template into a string
    with open(args.template) as f:
        config = "".join(f.readlines())

    if args.replace:
        # Parse key-value pairs provided
        mod = {}
        for pair in args.replace.split(","):
            elems = pair.split("=")
            if len(elems) != 2:
                raise ValueError("Unrecognized format for key-value pair '{}'".format(pair))
            k = elems[0]
            v = elems[1]
            mod[k] = v
    
        # Modify config template
        for k, v in mod.items():
            pattern = re.compile(r"^{}.+?\n".format(k), re.MULTILINE)
            config = pattern.sub("{} = {}\n".format(k,v), config)
    
    # Write modified config
    with open(args.output, "w") as f:
        f.write(config)
