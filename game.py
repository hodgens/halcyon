#BEHOLD THE BLANK PAGE
import re, sys
import pygame
from pygame.locals import *
from settings import *

# let's get the PyGame initialization out of the way
(numberpassed, numberfailed) = pygame.init()

main_screen = pygame.display.set_mode( [SCREEN_WIDTH, SCREEN_HEIGHT] )
exit_status = 0 # for quitting the main loop
center_box = pygame.Surface([SCREEN_WIDTH, SCREEN_HEIGHT])
center_box.fill((255,255,255))
main_screen.blit(center_box, (0,0))


# now for the actual Halcyon stuff
game_mode = 0
combat_mode = 0
map_mode = 1
player_ready = 0
update_count = 1
test_attribute = 14
#environment_file = open(sys.argv[1])
NPC_LIST = []
MOVEMENT_BUTTONS = []
UI_BUTTONS = [] 
SCREENS = []
MAPS = []
CURRENT_NODE = [None]
STORY_ELEMENTS = []
MAP_DISPLAY_KEYS = [K_w, K_a, K_s, K_d]
page_count = 0

# Start up the font object for text display
pygame.font.init()
Text_font = pygame.font.SysFont("C:\Windows\Fonts\04B_19_.TTF",FONT_SIZE)

class Settings:
	# this class will define the settings for buttons, so they can be reused easily
	def __init__(self, width, height, open_color, set_color, background_color, inactive_color, border_width):
		self.width = width
		self.height = height
		self.open_color = open_color # used to define base color
		self.set_color = set_color
		self.background_color = background_color
		self.border_width = border_width
		self.inactive_color = inactive_color

class Button:
	# this class takes the settings and actually sets up where the buttons are and what they say
	def __init__(self, x_pos = None, y_pos = None, button_settings = None, text = None, pygame_key_id = None):
		# for readability, I'm going to move the settings from the settings object into this object
		self.button_settings = button_settings
		self.width = self.button_settings.width
		self.height = self.button_settings.height
		self.open_color = self.button_settings.open_color
		self.set_color = self.button_settings.set_color
		self.background_color = self.button_settings.background_color
		self.border_width = self.button_settings.border_width
		self.current_color = self.open_color
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.pygame_key_id = pygame_key_id
		self.status = "open" # "open" means it hasn't been pressed, "set" means it's been pressed, and will be used as the next command on submit
		self.text = text # the default text you start with before the game tells it differently
		self.transient_text = None # this is what the game tells you to say
		
		if self.width is not None and self.height is not None and self.open_color is not None and self.background_color is not None and self.border_width is not None:
			self.button_surface = pygame.Surface((self.width,self.height))
			self.button_surface.fill(self.background_color)
			self.button_surface.fill(self.current_color,(self.border_width, self.border_width, self.width - 2* self.border_width, self.height - 2* self.border_width))

		if self.text is not None:
			# draw the text on the button
			self.button_text_image = Text_font.render(self.text,1,self.background_color)
			text_dimensions = Text_font.size(self.text)
			self.button_surface.blit(self.button_text_image,[self.width/2-text_dimensions[0]/2,self.height/2-text_dimensions[1]/2])
		main_screen.blit(self.button_surface,(self.x_pos,self.y_pos))


	def draw_self(self):
		self.button_surface.fill(self.current_color,(self.border_width, self.border_width, self.width - 2* self.border_width, self.height - 2* self.border_width)) # draw the empty button
		if self.transient_text is None:
			text_to_use = self.text
		else:
			text_to_use = self.transient_text
		text_dimensions = Text_font.size(text_to_use)
		self.button_text_image = Text_font.render(text_to_use,1,self.background_color)
		self.button_surface.blit(self.button_text_image,[self.width/2-text_dimensions[0]/2,self.height/2-text_dimensions[1]/2])
		main_screen.blit(self.button_surface,(self.x_pos,self.y_pos))
				

	def change_status(self, new_status): # this is used to switch between the "open" and "set" cases for drawing buttons
		global update_count
		update_count += 1
		if new_status is "set":
			self.status = "set"
			self.current_color = self.set_color
			print("changing color to "+str(self.set_color))
			self.draw_self()
			for each_button in MOVEMENT_BUTTONS:
				if each_button.pygame_key_id is not self.pygame_key_id and each_button.status is "set":
					each_button.change_status(new_status = "open")
					each_button.draw_self()
		elif new_status == "open":
			self.status = "open"
			self.current_color = self.open_color
			print("changing color to " +str(self.set_color))
			self.draw_self()
		else:
			sys.exit("You tried to set a button to something it can't be.")

	def set_text(self, text_to_set):
		# changes what text the button should display
		self.transient_text = text_to_set
		self.draw_self()


class Screen:
	def __init__(self, dimensions, background_color, foreground_color, text_color, border_width):
		# screens are just for displaying text
		self.x_pos = dimensions[0] # top left x coord
		self.y_pos = dimensions[1] # top left y coord
		self.width = dimensions[2]
		self.height = dimensions[3]
		self.border_width = border_width
		self.background_color = background_color
		self.foreground_color = foreground_color
		self.text_color = text_color
		self.outer_dimensions = dimensions
		self.inner_dimensions_and_position = [self.border_width, self.border_width, self.width - 2*self.border_width, self.height - 2*self.border_width] # this is used to specify the inner panel's placement when you're positioning it in the screen element
		self.inner_dimensions = [0,0,self.width - 2*self.border_width, self.height - 2*self.border_width] # this is used for placing and designing stuff on the inner panel before you pass it to the screen to be rendered
		
		# create a Pygame rect based on this info
		self.screen_image = pygame.Surface((self.width,self.height))
		self.screen_image.fill(self.background_color)
		self.screen_image.fill(self.foreground_color, self.inner_dimensions_and_position)
		# dimensions expect 
		#self.draw_self(1,0)
		main_screen.blit(self.screen_image,(self.x_pos,self.y_pos))
		
	def check_length(self, text, image_width):
		text_size = Text_font.size(text)
		text_width = text_size[0]
		if text_width > image_width:
			return False # text width greater than image width
		else:
			return True # text width less than image width

	def wrap_text(self, text, image_width):
		# take in text, return a list of wrapped text
		wrapped_text = []
		if self.check_length(text, image_width) is True:
			wrapped_text.append(text)
			
		string_front_half = ""
		string_back_half = text
		
		while self.check_length(string_back_half, image_width) is False:
			string_front_half = string_front_half + string_back_half[0]
			string_back_half = string_back_half[1:]
			if self.check_length(string_front_half, image_width) is True:
				continue
			else:
				# back up a letter
				while string_front_half[-1] is not " ":
					string_back_half = string_front_half[-1] + string_back_half
					string_front_half = string_front_half[0:-1]
				wrapped_text.append(string_front_half)
				string_front_half = ""
			wrapped_text.append(string_front_half) # because we still have the front half laying around
		return wrapped_text

	def get_attribute_description(self, character_name, attribute_name):
		attribute_description = None
		for each_npc in NPC_LIST:
			if each_NPC.name == character_name:
				#check attribute flavor text for the current attribute
				value_to_check = each_NPC.attribute_name
				# THIS IS VERY NONFUNCTIONAL
		if attribute_description is not None:
			return attribute_description
		else:
			sys.exit("You tried to reference a character that doesn't exist")
		
	def display_text(self, text):
		# this is the function you call when you want to tell a screen to display a piece of text
		# you don't call it directly, though, you tell the screen to use draw_self() and it looks at the current game state and the map node's story elements
		lines_to_display = self.wrap_text(text,self.width - 4*self.border_width)
		if lines_to_display is not None:
			line_counter = 0
			self.text_image = pygame.Surface([self.width - 2*self.border_width, self.height - 2*self.border_width])
			for each_line in lines_to_display:
				line_image = Text_font.render(each_line,1,self.background_color)
				line_dimensions = Text_font.size(each_line)
				self.text_image.blit(line_image, [Text_font.get_linesize(), Text_font.get_linesize() + line_counter * Text_font.get_linesize()])
				line_counter += 1
			self.screen_image.fill(self.foreground_color)
			self.screen_image.blit(self.text_image,self.inner_dimensions_and_position)
	
	def draw_self(self, text_to_draw):
		# this takes text, renders it using internal functions, pastes it on the screen, and tells the game to update the screen
		self.display_text(text_to_draw)
		global update_count
		update_count += 1
		main_screen.blit(self.screen_image,(self.x_pos,self.y_pos))
		# put together a scroll widget that I can use to inform the screen of how to position the text
	
class Map:
	def __init__(self):
		# any attribute name you use here has to match how it will be written in the spec file
		self.Node_Name = None
		self.NPCs = None # expected to be a list of strings if present
		self.Items = None
		self.effects = None # if you want to do something like, the room takes away five health per turn
		self.map_paths = None # expected to be a list of strings if present
		self.Flags = None
		self.Descriptive_Text = None
		self.Destinations = None # expected to be a list
		self.page_number = 0 # for deciding which destinations to display if you have too many
		self.Story_Elements = None

	def __eq__(self, target):
		if self.Node_Name == target:
			return True
		else:
			return False

	def make_lists(self):
		if self.map_paths is not None:
			self.map_paths = self.map_paths.split(",")
		if self.Destinations is not None:
			self.Destinations = self.Destinations.split(",")
		if self.NPCs is not None:
			self.NPCs = self.NPCs.split(",")
	
	def get_destinations(self):
		# since we can only display four directions at a time
		# but we may have more than four directions to display
		# we need to check how many directions we have and choose which ones to send
		if len(self.Destinations) <= len(MAP_DISPLAY_KEYS):
			names_to_return = self.Destinations
		else:
			start_point = 0 + self.page_number*len(MAP_DISPLAY_KEYS)
			end_point = len(MAP_DISPLAY_KEYS) + self.page_number*len(MAP_DISPLAY_KEYS)
			if end_point > len(self.Destinations):
				end_point = len(self.Destinations)
			names_to_return = self.Destinations[start_point:end_point]
		while len(names_to_return) < len(MAP_DISPLAY_KEYS):
			names_to_return.append("")
		dict_to_return = {each:names_to_return[MAP_DISPLAY_KEYS.index(each)] for each in MAP_DISPLAY_KEYS}
		return dict_to_return

	def turn_destinations_page(self):
		if len(self.Destinations) >= len(MAP_DISPLAY_KEYS) and len(self.Destinations) - self.page_number*len(MAP_DISPLAY_KEYS) < len(MAP_DISPLAY_KEYS):
			self.page_number = 0
		else:
			self.page_number += 1

	def get_text(self):
		if self.Story_Elements is None:
			return self.Descriptive_Text
		for each_story in self.Story_Elements:
			story_factors = each_story.get_story_text()
			if story_factors is not None:
				return story_factors
		return self.Descriptive_Text


class StoryElement:
	def __init__(self, element_name, paths = None):
		self.element_name = element_name
		self.paths = paths # is a list of the names of the paths
		# the story element keeps track of the paths and their prerequisites
	def choose_path(self):
		# this is an internal function that looks at the story's content and chooses which branch
		if len(self.paths) is 1:
			return self.paths[0]
		evaluate_strings = lambda x: exec(x)
		for each_path in self.paths:
			if all([eval(each_string) for each_string in getattr(self,each_path+"_Prerequisites")]):
            # the prerequisites are stored as strings, evaluate the strings
                		return each_path
		return None
	def get_story_text(self):
		# this is what you call when you want to get story text from the element
		story_to_use = self.choose_path()
		print(story_to_use)
		if story_to_use is not None:
			text_to_display = getattr(self,story_to_use)["Story_Content"]
			effects_to_enact = getattr(self,story_to_use)["Effects"]
			buttons_to_display = getattr(self,story_to_use)["Buttons"]
			return [text_to_display, effects_to_enact, buttons_to_display]
		else:
			return None
			
		# look at your stored story paths
		# if there's only one, then do the appropriate stuff: send the text to the screen, modify buttons, change game state, etc
		# if there's more than one, check the prerequisites for each
		x=1
	def make_lists(self):
		if self.paths is not None:
			self.paths = self.paths.split(",")
		for each_attribute in dir(self):
			if re.search("button",str(each_attribute), re.IGNORECASE):
				self.each_attribute = self.each_attribute.split(";")
				temp_dict = {}
				for each_item in self.each_attribute:
					[key_id,text] = each_item.split("|")
					temp_dict[key_id] = text
				if temp_dict is not {}:
					self.each_attribute = temp_dict
		valueof = lambda x: getattr(self,each_pathname + x)
		for each_pathname in self.paths:
			self.each_pathname = {"Story_Content":valueof("_Story_Content"), "Effects":valueof("_Effects"), "Buttons":valueof("_Buttons")}
		
class AI_settings:
	# this class will be used to set what the playstyles of the NPCs are	
	# for example, some NPCs may be a caster type, and biased toward magic use
	def __init__(self, style):
		self.style=style

class Character:
	# this class holds the information about where the NPCs are and what they're holding and how to move them
	def __init__(self, name, location, AI_component = None):
		self.name = name
		self.location = location
		self.AI_component = AI_component
		self.target = None
		self.initiative = None
		self.character_image = None
		self.flavor_text = None # characters hold their own flavor text
		self.inventory = None
	def move_character(self, new_location):
		current_node = None
		taret_node = None
		for each_location in MAPS:
			if each_location.__eq__(self.location):
				current_node = each_location
			if each_location.__eq(new_location):
				target_node = each_location
		if current_node is None:
			sys.exit("the character can't leave the formless void")
		if target_node is None:
			sys.exit("the character cannot enter the formless void")

		can_move = 0	
		for each_path in current_node.exits:
			if each_path == new_location:
				can_move = 1
		if can_move is not 0:
			self.location = target_node.Node_Name
			target_node.NPCs.append(self.name)
			current_node.NPCs.remove(self.name)
			CURRENT_NODE[0] = target_node
		# check that route between current and new location exists
		# add character to list of characters in the new location
		# remove character from list of characters in old location
	def calc_initiative_target(self, possible_targets):
		z=1
		# calculate your initiative based on stats
		# choose target from possible targets
	def load_flavor_text(self):
		# go through flavor text file, add all flavor text that matches your character name to this object
		x=1


		
# this function will read in the environment nodes and store them as code objects
def parse_node_file(filename, node_storage, node_type):
	file = open(filename)
	internal_check = 0
	if node_type is "map":
		Node_type = Map
		current_line = ""
		for line in file:
			line = line.rstrip('\n')
			if re.search("{",line):
				current_node = Map()
				internal_check += 1
			if re.search("\[",line):
				current_text = ""
				current_name = ""
				current_line = ""
				internal_check += 1
			current_line += line
			#print(current_line)
			if re.search("\]",line):
				name_search = re.search("\[(.+?):",current_line)
				if name_search is None:
					sys.exit("Your game file has no element name I can see")
				current_name = name_search.group(1)
			#	print("current name is "+str(current_name))
				content_search = re.search(":(.+?)\]",current_line)
				if content_search is None:
					sys.exit("Your game file has no element content I can see")
				current_text = content_search.group(1)
			#	print("current content is "+str(current_text))
				current_node.__setattr__(current_name, current_text)
				internal_check -= 1
			if re.search("}",line):
				current_node.make_lists()
				node_storage.append(current_node)
				current_node = None
				internal_check -= 1
				if internal_check is not 0:
					sys.exit("Your game file has mismatched delimiters")
	elif node_type is "story":
		# HOLY WOW THIS IS BROKEN RIGHT NOW
		Node_type = StoryElement
		current_line = ""
		# HOW AM I GOING TO STORE THE MULTIPLE PATH INFORMATION?
		# MAYBE BY MAKING A DICT WITH TUPLES AS THE VALUES?
		for line in file:
			line = line.rstrip('\n')
			if re.search("{",line):
				current_node = Map()
				internal_check += 1
			if re.search("\[",line):
				current_text = ""
				current_name = ""
				current_line = ""
				internal_check += 1
			current_line += line
			#print(current_line)
			if re.search("\]",line):
				name_search = re.search("\[(.+?):",current_line)
				if name_search is None:
					sys.exit("Your game file has no element name I can see")
				current_name = name_search.group(1)
				#print("current name is "+str(current_name))
				content_search = re.search(":(.+?)\]",current_line)
				if content_search is None:
					sys.exit("Your game file has no element content I can see")
				current_text = content_search.group(1)
				#print("current content is "+str(current_text))
				current_node.__setattr__(current_name, current_text)
				internal_check -= 1
			if re.search("}",line):
				current_node.make_lists()
				node_storage.append(current_node)
				current_node = None
				internal_check -= 1
				if internal_check is not 0:
					sys.exit("Your game file has mismatched delimiters")
		

# These are the settings for regular UI interaction buttons
direction_combat_button_settings = Settings(width=BUTTON_WIDTH, height = BUTTON_HEIGHT, inactive_color = BUTTON_INACTIVE_COLOR, open_color = BUTTON_OPEN_COLOR, set_color = BUTTON_SET_COLOR, background_color = BUTTON_BACKGROUND_COLOR, border_width = BUTTON_BORDER_WIDTH)
non_interactive_button_settings = Settings(width = BUTTON_WIDTH, height = BUTTON_HEIGHT, inactive_color = BUTTON_OPEN_COLOR, open_color = BUTTON_OPEN_COLOR, set_color = BUTTON_OPEN_COLOR, background_color = BUTTON_BACKGROUND_COLOR, border_width = BUTTON_BORDER_WIDTH)


w_button = Button(x_pos = 255, y_pos = 362, text = "North", button_settings = direction_combat_button_settings, pygame_key_id = K_w)
a_button = Button(x_pos = 130, y_pos = 393, text = "West", button_settings = direction_combat_button_settings, pygame_key_id = K_a)
s_button = Button(x_pos = 255, y_pos = 393, text = "South", button_settings = direction_combat_button_settings, pygame_key_id = K_s)
d_button = Button(x_pos = 375, y_pos = 393, text = "East", button_settings = direction_combat_button_settings, pygame_key_id = K_d)
q_button = Button(x_pos = 130, y_pos = 362, text = "Examine", button_settings = non_interactive_button_settings, pygame_key_id = K_q)
f_button = Button(x_pos = 500, y_pos = 393, text = "Confirm", button_settings = non_interactive_button_settings, pygame_key_id = K_f)
tab_button = Button(x_pos = 5, y_pos = 362, text = "Page", button_settings = non_interactive_button_settings, pygame_key_id = K_TAB)

MOVEMENT_BUTTONS.extend([w_button,a_button,s_button,d_button])
UI_BUTTONS.extend([f_button, tab_button, q_button])

Main_Interface_Screen = Screen([10,10,600,200], background_color=BUTTON_BACKGROUND_COLOR, foreground_color=BUTTON_OPEN_COLOR, text_color=[0,0,0], border_width=10)
SCREENS.append(Main_Interface_Screen)
	
# main strategy for game handling:
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

# it calls the appropriate button based on the key input
# it's agnostic to what the buttons actually do or what's being displayed on screen
# the buttons call handler functions that perform the proper actions mased on checking the combat_mode and map_mode flags

def set_up_all_buttons(dict_of_buttons_to_change):
	# this function takes a list of keys to change and the text they should be changed to, and changes them
	# it sets all other buttons to be greyed out
	# it expects a dict containing the button to change and the new text to assign to it
	global MOVEMENT_BUTTONS
	for each_key in dict_of_buttons_to_change: # each_key is an integer, representing the key ID
		counter = 0
		for each_button in MOVEMENT_BUTTONS: # each_button is an object of the Button class
			if each_key == each_button.pygame_key_id:
				# i need the index in movement buttons of the object wiht id == key
				MOVEMENT_BUTTONS[counter].set_text(dict_of_buttons_to_change[each_key])
			counter += 1
	global update_count
	update_count += 1

def map_turn(action, target=None):
	# map_turn() is the main non-combat function that controls the game.
	# this function will perform movement by changing game state and switching player position in the map node collection
	# it will also facilitate environment/npc interactions by invoking the story objects associated with the current map node
	if action is not None:
		print(action)
	if map_mode == 0:
		return None
	if action == "move":
		CURRENT_NODE[0].page_number = 0
		#move player
	
		if len(CURRENT_NODE) is not 0: # ask the map what story elements it has, ask for a story
			if CURRENT_NODE[0].Story_Element_Names is not None:
				current_story_info = CURRENT_NODE[0].get_story_text()
				text_to_draw = current_story_info[0]
				effects_to_enact = current_story_info[1]
				buttons_to_draw = current_story_info[2]
				set_up_all_buttons(buttons_to_draw)
				Main_Interface_Screen.draw_self(text_to_draw)
				if effects_to_enact is not None:
					effects_list = effects_to_enact.split(";")
					for each_effect in effects_list:
						exec(each_effect)
			else:
				text_to_draw = CURRENT_NODE[0].Descriptive_Text
				Main_Interface_Screen.draw_self(text_to_draw)
		else:
			text_to_draw = "lol placeholder"
	elif action == "examine" and target is None:
		x=1
		#examine the map node
	elif action == "examine" and target is not None:
		x=2
		#examine an object
	elif action == "inventory":
		x=2
		#open inventory menu
	elif action == "change page":
		print("changing page")
		CURRENT_NODE[0].turn_destinations_page()	
		new_placenames = CURRENT_NODE[0].get_destinations()
		set_up_all_buttons(new_placenames)

	# figure out what buttons to draw

	#Main_Interface_Screen.draw_self(text_to_draw) # this doesn't belong here yet, it's not appropriate

def process_turn(combat_mode, map_mode, player_action = None, target = None, ready_mode = 0):
	# ready_mode determines whether the player is ready for a game update
	# if the player is ready, process_turn() invokes map_turn(), which either looks at the current map node (if it's a non-movement action that needs to be performed) for text to display, or moves the player and then looks to the map node
	if combat_mode not in [0,1] or map_mode not in [0,1] or ready_mode not in [0,1] or combat_mode == map_mode:
		print("map mode is "+str(map_mode))
		print("combat mode is "+str(combat_mode))
		print("ready_mode is "+str(ready_mode))
		sys.exit("Your game control logic is faulty")
	
	if combat_mode is 1:
		x=1
		# get all present entities from the current map node
		# pass them to combat_turn
	elif map_mode is 1 and ready_mode is 1:
		map_turn(player_action, target)



Player = Character(name = "Player", location = None)

parse_node_file("map.txt",MAPS,node_type="map")
for each_map_node in MAPS:
	if "Player" in each_map_node.NPCs:
		CURRENT_NODE[0] = each_map_node
		Player.location = CURRENT_NODE[0].Node_Name
		Main_Interface_Screen.draw_self(each_map_node.Descriptive_Text)

if CURRENT_NODE[0] is None:
	sys.exit("You never defined a starting place for the player")

parse_node_file("story_elements.txt",STORY_ELEMENTS,node_type="story")

starting_dests = CURRENT_NODE[0].get_destinations()
#print(starting_dests)
set_up_all_buttons(starting_dests)

map_mode = 1
combat_mode = 0
ready_mode = 0
target = None
while exit_status is 0:
	next_event = pygame.event.poll()
	action = None
	target = None
	if next_event == pygame.NOEVENT:
		continue
	if next_event.type == KEYDOWN and next_event.key == K_ESCAPE:
		exit_status = 1
	if next_event.type == KEYDOWN and next_event.key == K_c:
		center_box.fill((100,200,100))
		main_screen.blit(center_box, (0,0))
	if next_event.type == KEYDOWN and next_event.key == K_w:
		w_button.change_status("set")
		if map_mode == 1:
			action = "move_up"
		elif combat_mode == 1:
			action="light_attack"
	if next_event.type == KEYDOWN and next_event.key == K_a:
		a_button.change_status("set")
		action = "move_left"	
	if next_event.type == KEYDOWN and next_event.key == K_s:
		s_button.change_status("set")
		if map_mode == 1:
			action = "move_down"
		elif combat_mode == 1:
			action = "heavy_attack"
	if next_event.type == KEYDOWN and next_event.key == K_d:
		d_button.change_status("set")
		action = "move_right"	
	if next_event.type == KEYDOWN and next_event.key == K_q and combat_mode == 1:
		q_button.change_status("set")
		action = "block"
	if next_event.type == KEYDOWN and next_event.key == K_e and combat_mode == 1:
		e_button.change_status("set")
		action = "parry"
		
	if next_event.type == KEYDOWN and next_event.key == K_x:
		action = "examine_node"
		# pop up menu to choose target
		# call .get_most_recent_story(current_node) on the node
	
	if next_event.type == KEYDOWN and next_event.key == K_z:
		action = "examine"
		# pull up the menu to choose an item
	
	if next_event.type == KEYDOWN and next_event.key == K_TAB:
		print("tab seen")
		action = "change page"
		# pull up the menu to choose an item
	if action is not None:
		ready_mode = 1

	process_turn(combat_mode = combat_mode, map_mode = map_mode, player_action=action, target = target, ready_mode = ready_mode)
	# process_turn() looks at the game state and decides what to do
		
	if update_count is not 0:
		pygame.display.flip() #flip updates the main_screen to the actual displayscreen
		update_count = 0

pygame.quit()
