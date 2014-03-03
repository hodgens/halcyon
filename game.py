#BEHOLD THE BLANK PAGE
import re

environment_file = open(sys.argv[1])

SAVED_NODES = []

class NodeBuffer:
	def __init__(self):
		self.Node_contents = None # for storing all the original specifications of the Node
		self.Clean_node_contents = []
		self.Story_elements = [] # list of Story objects
		self.Map_image = None # filename for map to display
		self.Character_image = None # filename for character display
		self.Element_Names = None
		
	def add_line(self,line):
		self.Node_contents.append(line)
		self.Clean_node_contents.append(line.rstrip())
		
	def parse_node(self):
		# go through the node, split up elements
		current_story_element_name = ""
		current_story_element_content = ""
		for line in self.Clean_node_contents:
			# look for the pattern showing the start of an element
			# regex explanation: search for characters, at least one, in a non-greedy fashion, occurring between a left square bracket character and a colon.
			name_search = re.search("\[(.+?):",line)
			if name_search:
				# start new node
				current_story_element_name = line_search.group(1)
			# the above will only happen if the current line contains a new element declaration
			
			
			content_search = re.search(":(.+?)\]",line)
			if content_search is None:
				non_ending_content = re.search(":(.+?)
				current_story_element_content += 
			# the above will only happen if the current line does not contain the end of the new element declaration	
			
			# if you see the end character for a node block
			if re.search("\]",line):
				current_node.add_line(line)
				# clean up the newline characters, save the node 
				current_story_element_name = current_story_element_name.rstrip()
				#append
				current_node = ""
			# the above will only happen if the current line ends the story element delcaration
		
		
def parse_node_file(file, node_storage):
	# read in file
	# go through the file, parse out the different node contents
	# create a new node object appropriately
	# add the node object to the list
	
	# create a new Node object when you first hit the node opening bracket
	# assign it to a current working node
	# progress through the Node specification
	# move node to list of finished nodes when you reace the node closing bracket
	
	for line in file:
		# if you see a new node start
		if re.search("{",line):
			# start new node
			current_node = NodeBuffer()
		
		# if you see the end character for a node block
		if re.search("}",line):
			current_node.add_line(line)
			# clean up the newline characters, save the node 
			current_node.parse_node()
			SAVED_NODES.append(current_node)
			current_node = None
		
		# if you don't see an end character anywhere (in the middle of a node block)	
		if re.search("}") is None and current_node is not None:
			current_node.add_line(line)