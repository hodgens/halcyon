#BEHOLD THE BLANK PAGE
import re
import pygame
from pygame.locals import *
from settings import *

# let's get the PyGame initialization out of the way
(numberpassed, numberfailed) = pygame.init()

main_screen = pygame.display.set_mode( [SCREEN_WIDTH, SCREEN_HEIGHT] )
exit_status = 0 # for quitting the main loop
center_box = pygame.Surface((20,20))
center_box.fill((100,125,255))
main_screen.blit(center_box, (0,0))

# now for the actual Halcyon stuff
#environment_file = open(sys.argv[1])
SAVED_NODES = []

# now a dict to store the different command states for the UI
# "open" means it hasn't been pressed.
# "set" means it's been pressed, and will be used as the next command on submit
# this isn't a set in stone thing, it's just a proof of concept
KEY_COMMAND_STATUS = {K_w:"open", K_a:"open", K_s:"open", K_d:"open", K_q:"open", K_e:"open", K_f:"open"}

# Since we're going to be making multiple types of buttons, with multiple instances of each type,
# let's make a settings class we can plug into the buttons module
# to make a new button, you just specify the settings object and give it text and x,y position (top left corner)

# Let's start up the font object
pygame.font.init()
Text_font = pygame.font.SysFont("C:\Windows\Fonts\04B_19_.TTF",FONT_SIZE)

# this class will define the settings for buttons, so settings can be reused easily
class Settings:
	def __init__(self, width, height, open_color, set_color, background_color, border_width):
		self.width = width
		self. height = height
		self.open_color = open_color # used to define base color
		self.set_color = set_color
		self.background_color = background_color
		self.border_width = border_width

# this class takes the settings and actually sets up where the buttons are and what they say
class Button:
	def __init__(self, x_pos = None, y_pos = None, button_settings = None, text = None, action = None):
		# for readability, I'm going to move the settings from the settings object into this object
		self.button_settings = button_settings
		self.text = text
		self.width = self.button_settings.width
		self.height = self.button_settings.height
		self.open_color = self.button_settings.open_color
		self.set_color = self.button_settings.set_color
		self.background_color = self.button_settings.background_color
		self.border_width = self.button_settings.border_width
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.button_settings = None # how big is it, what color is it, that stuff
		self.action = action # the function the button performs when it's pressed by the user
		
		if self.width is not None and self.height is not None and self.open_color is not None and self.background_color is not None and self.border_width is not None:
			self.button_surface = pygame.Surface((self.width,self.height))
			self.button_surface.fill(self.background_color)
			self.button_surface.fill(self.open_color,(self.border_width, self.border_width, self.width - self.border_width, self.height - self.border_width))
		if self.text is not None:
			# draw the text on the button
			self.button_text_image = Text_font.render(text,1,self.background_color)
			self.button_surface.blit(self.button_text_image,[1,1])
	def set_state(self,state):
		x=1
		# switch state from open to set, if applicable

# this class holds all the information about the different environment nodes and the connected story content	
class MapNode:
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
				non_ending_content = re.search(":(.+?)")
				current_story_element_content += non_ending_content
			# the above will only happen if the current line does not contain the end of the new element declaration	
			
			# if you see the end character for a node block
			if re.search("\]",line):
				current_node.add_line(line)
				# clean up the newline characters, save the node 
				current_story_element_name = current_story_element_name.rstrip()
				#append
				current_node = ""
			# the above will only happen if the current line ends the story element delcaration

# this class will be used to set what the playstyles of the NPCs are			
class AI_settings:
	def __init__(self, style):
		self.style=style

# this class holds the information about where the NPCs are and what they're holding and how to move them		
class Character:
	def __init__(self, location, AI_component = None):
		self.location = location
		self.AI_component = AI_component
	def move_character(self, new_location):
		x=1
		# check that route between current and new location exists
		# add character to list of characters in the new location
		# remove character from list of characters in old location

# this function will read in the environment nodes and store them as code objects
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
			
			
# strategy for button image handling:
# buttons start Color1 (white, say), then when they're pressed they turn Color2 (blue?)
# and then when you release, they turn Color3 (light blue?) to signify that that button is set to send
# once you submit the command for that round, the buttons reset to normal

# this is hte settings for regular UI interaction buttons
direction_combat_button_settings = Settings(width=BUTTON_WIDTH, height = BUTTON_HEIGHT, open_color = BUTTON_OPEN_COLOR, set_color = BUTTON_SET_COLOR, background_color = BUTTON_BACKGROUND_COLOR, border_width = BUTTON_BORDER_WIDTH)

w_button = Button(x_pos = 1, y_pos = 1, button_settings = direction_combat_button_settings, text = "w")

a_button = Button(x_pos = 20, y_pos = 20, button_settings = direction_combat_button_settings, text = "a")

s_button = Button(x_pos = 40, y_pos = 40, button_settings = direction_combat_button_settings, text = "s")

d_button = Button(x_pos = 60, y_pos = 60, button_settings = direction_combat_button_settings, text = "d")
	
# main strategy for game handling:
# tasks in map node:
# 1. check for user input - player can examine an entity or interact with it
# when the player does, check the entity's associated properties to see what should be done
# 2. check the map node's associated story elements
# go to most recent story element, display as needed
# 3. player may initiate combat with an entity
# if so, go to combat mode

# when you first enter a node, check to see if there's hostile NPCs present
# if there are, set combat_mode=1
# while in combat mode, check to see if the timer flag is set, and what the time
# every loop, check the time and make sure you're under it.
# check for player input, and when you detect player input, start figuring out NPC combat actions
# apply actions, re-loop

# if there's not hostile NPCs, then enter map mode
# when you enter map mode, check the current map node, and look at its stories
# find the youngest unlocked story element, display it (unless it has a display_once flag set)
# if there are none, default to the basic node description

combat_mode = 0
map_mode = 1

# the main loop just polls the keyboard for events
# it calls the appropriate button based on the key input
# it's agnostic to what the buttons actually do or what's being displayed on screen
# the buttons call handler functions that perform the proper actions mased on checking the combat_mode and map_mode flags
while exit_status is 0:
	next_event = pygame.event.poll()
	if next_event == pygame.NOEVENT:
		continue
	if next_event.type == KEYDOWN and next_event.key == K_ESCAPE:
		exit_status = 1
	if next_event.type == KEYDOWN and next_event.key == K_c:
		center_box.fill((100,200,100))
		main_screen.blit(center_box, (0,0))
		
	pygame.display.flip() #flip updates the main_screen to the actual displayscreen

pygame.quit()