import csv
import argparse

NAME_INDEX = 1
SET_INDEX = 0
NUMBER_INDEX = 3
FULL_INDEX = 2

DEFAULT_CONDITION = "Near Mint"
DEFAULT_LANGUAGE = "English"

class Format():
    def __init__(self, name, has_header, name_index, set_index, language_index, condition_index, collector_index, foil_index):
        self.name = name
        self.has_header = has_header
        self.name_index = name_index
        self.set_index = set_index
        self.language_index = language_index
        self.condition_index = condition_index
        self.collector_index = collector_index
        self.foil_index = foil_index

Format.Delverlens = Format('delverlens', True, 2, 3, 6, 5, 4, 7)
Format.Deckbox = Format('deckbox', True, 2, 3, 6, 5, 4, 7)

def load(format, filename):
    header = None
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        if format.has_header:
            header = next(reader)
        return header, list(reader)

def parse_rule(rule):    
    rule = rule.strip()
    if rule[0] == '{':
        names = [m.strip() for m in rule[1:rule.index('}')].split('|')]
        set_rep = rule[rule.index('}'):].split('|')[1].split('->')
        #print(set_rep)
        rhs = set_rep[1].strip()
        lhs = set_rep[0].strip()
        return [[[n, lhs], [n, rhs]] for n in names], True

    if '|' in rule:
        return [[m.strip() for m in s.split('|')] for s in rule.split("->")], False
    else:
        return [s.strip() for s in rule.split("->")], False

def flatten_rules(rules):
    final = []
    for s in rules:
        if "->" not in s:
            continue
        parsed, res = parse_rule(s)
        final += parsed if res else [parsed]
    return final
  
def get_rules_file(file_from, to):
    with open(file_from + '-to-' + to + '.con') as file:
        lines = [x.strip() for x in file.readlines()]
        lines = list(filter(None, lines))
        set_index = lines.index('SET_REPLACE')
        name_index = lines.index('NAME_REPLACE')
        full_index = lines.index('NAME_SET_REPLACE')
        number_index = lines.index('NAME_NUMBER_REPLACE')
        
    return (flatten_rules(lines[set_index:name_index]), \
        flatten_rules(lines[name_index:full_index]), \
        flatten_rules(lines[full_index:number_index]), \
        flatten_rules(lines[number_index:]))

def replace(line, rules, format, dest):
    def matches_rule(x, rule):
        for r in rule:
            if r[0] == x:
                return r[1]
        return x
    if len(line) == 0:
        return line #ignore empty
    newline = line[:]
    name, ed = newline[format.name_index].strip(), newline[format.set_index].strip()

    #some special hard-coded rules go here

    #cardsphere wants numbered lands
    if name in ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"] and dest == "cardsphere" and ed != "Unhinged" and ed != "Unstable" and ed != "Theros Beyond Death":
        name = name + " (#" + newline[format.collector_index] + ")"
        name = matches_rule([name, ed], rules[FULL_INDEX])[0]

    if name in ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"] and dest == "cardsphere" and ed in ["Battle for Zendikar", "Unhinged", "Unstable", "Theros Beyond Death", "Hour of Devastation"]:
        name += " (Full Art)"


    if format.name == "deckbox" and dest == "deckbox":
        newline[1] = newline[0]

    #main bulk here
    newline[format.name_index] = matches_rule(name, rules[NAME_INDEX])
    newline[format.set_index] = matches_rule(ed, rules[SET_INDEX])
    
    if dest == "cardsphere":
        #cardsphere prerelease promos
        if ed.startswith("Prerelease Events"):
            newline[format.set_index] = "Prerelease Promos"
        
        if ed == "War of the Spark Japanese Alternate Art":
            newline[format.name_index] += " (Alternate Art)"
            newline[format.set_index] = "War of the Spark"

        if ed.startswith("World Championship"):
            year_name = ed.split(": ", 1)[1]
            year, n = year_name.split(",")  
            newline[format.name_index] += " (" + n.strip() + " " + year + ")"
            newline[format.set_index] = "World Championship"
        
        if ed == "Double Masters" and int(newline[format.collector_index]) >= 333:
            newline[format.set_index] = "Double Masters Box Toppers"
    #delverlens language conversion
    if format.name == "delverlens":
        if newline[format.language_index] == "Chinese Simplified":
            newline[format.language_index] = "Chinese"
        elif newline[format.language_index] == "Chinese Traditional":
            newline[format.language_index] = "Traditional Chinese" 

    #fill in missing conditions
    if format.condition_index is not None and newline[format.condition_index] == "":
        newline[format.condition_index] = DEFAULT_CONDITION
    if format.language_index is not None and newline[format.language_index] == "":
        newline[format.language_index] = DEFAULT_LANGUAGE

    if format.collector_index is not None:
        newline[format.name_index] = matches_rule([newline[format.name_index], newline[format.collector_index]], rules[NUMBER_INDEX])[0]

    newline[format.name_index], newline[format.set_index] = matches_rule([newline[format.name_index], newline[format.set_index]], rules[FULL_INDEX])
    return newline

def reconstruct(header, lines, filename):
    with open(filename, 'w+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer = csv.writer(file,quoting=csv.QUOTE_ALL)
        writer.writerows(lines)

if __name__ == "__main__":

    
    parser = argparse.ArgumentParser(description='Convert one MTG csv file from one format to another.')
    parser.add_argument("filename", help="path to the csv file to convert")
    parser.add_argument('inputformat', help='the format to convert from')
    parser.add_argument('outputformat', help='the format to convert to')
    parser.add_argument("outputfile", help="path to the output file")
    args = parser.parse_args()
    print(args.inputformat)
    format = Format.Delverlens if args.inputformat == "delverlens" else Format.Deckbox
    out = args.outputformat
    header, inputs = load(format, args.filename)
    rules = get_rules_file(format.name, out)
    #print(rules)
    #print(inputs[0])
    outputs = [replace(line, rules, format, out) for line in inputs]
    #print(outputs[50])
    reconstruct(header, outputs, args.outputfile)
    count = 0
    for i, o in zip(inputs, outputs):
        if i != o:
            print("{0} ({1}) -> {2} ({3})".format(i[format.name_index], i[format.set_index], o[format.name_index], o[format.set_index]))
            count +=1
    print(str(count) + " converted!")
    print("Saved to {0}".format(args.outputfile))