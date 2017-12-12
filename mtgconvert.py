import csv
import argparse

NAME_INDEX = 1
SET_INDEX = 0
NUMBER_INDEX = 3
FULL_INDEX = 2

class Format():
	def __init__(self, name, has_header, name_index, set_index, language_index, condition_index, collector_index):
		self.name = name
		self.has_header = has_header
		self.name_index = name_index
		self.set_index = set_index
		self.language_index = language_index
		self.condition_index = condition_index
		self.collector_index = collector_index

Format.Delverlens = Format('delverlens', True, 2, 3, 6, 5, 4)
Format.Deckbox = Format('deckbox', True, 2, 3, 6, 5, 4)

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
		if res:
			final += parsed
		else:
			final += [parsed]
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
	#if len(line) == 0:
	#	return line #ignore empty
	newline = line[:]
	name, ed = newline[format.name_index].strip(), newline[format.set_index].strip()

	#deckbox wants different land format
	#of course, unhinged is special
	if name in ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"] and dest == "cardsphere" and ed != "Unhinged":
		name = name + " (#" + newline[format.collector_index] + ")"
		name = matches_rule([name, ed], rules[FULL_INDEX])[0]
		print(name)



	new_name = matches_rule(name, rules[NAME_INDEX])
	new_set = matches_rule(ed, rules[SET_INDEX])
	

	#delverlens language conversion
	if format.name == "delverlens":
		if newline[format.language_index] == "Chinese Simplified":
			newline[format.language_index] = "Chinese"
		elif newline[format.language_index] == "Chinese Traditional":
			newline[format.language_index] = "Traditional Chinese" 

	#fill in missing conditions
	if format.condition_index is not None and newline[format.condition_index] == "":
		newline[format.condition_index] = "Near Mint"
	if format.language_index is not None and newline[format.language_index] == "":
		newline[format.language_index] = "English"

	newline[format.name_index], newline[format.set_index] = matches_rule([new_name, new_set], rules[FULL_INDEX])
	if format.collector_index is not None and ed in ['Alliances', 'Homelands', 'Portal']:
		newline[format.name_index] = matches_rule([newline[format.name_index], newline[format.collector_index]], rules[NUMBER_INDEX])[0]
		if "(" in newline[format.name_index]:
			print(newline[format.name_index])

	return newline

def reconstruct(header, lines, filename):
	print(len(lines))
	with open(filename, 'w+', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(header)
		writer = csv.writer(file,quoting=csv.QUOTE_ALL)
		writer.writerows(lines)

if __name__ == "__main__":

	'''
	parser = argparse.ArgumentParser(description='Convert one MTG csv file from one format to another.')
	parser.add_argument("filename", help="path to the csv file to convert")
	parser.add_argument('from', help='the format to convert from')
	parser.add_argument('to', help='the format to convert to')
	parser.add_argument("outputfile", help="path to the output file")
	args = parser.parse_args()
	print(args['from'])
	'''
	format = Format.Delverlens
	header, inputs = load(format, 'inv.csv')
	rules = get_rules_file('deckbox', 'cardsphere')
	#print(rules)
	#print(inputs[0])
	outputs = [replace(line, rules, format, 'cardsphere') for line in inputs]
	print(outputs[50])
	reconstruct(header, outputs, 'output.csv')
	count = 0
	for i, o in zip(inputs, outputs):
		if i != o:
			print(i[format.name_index], i[format.set_index], o[format.name_index], o[format.set_index])
			count +=1
	print(str(count) + " converted!")	