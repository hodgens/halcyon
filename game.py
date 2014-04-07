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

#environment_file = open(sys.argv[1])
NPC_LIST = []
BUTTONS = []
SCREENS = []
MAPS = []
CURRENT_NODE = []
STORY_ELEMENTS = []

# Start up the font object for text display
pygame.font.init()
Text_font = pygame.font.SysFont("C:\Windows\Fonts\04B_19_.TTF",FONT_SIZE)

# this class will define the settings for buttons, so they can be reused easily
class Settings:
	def __init__(self, width, height, open_color, set_color, background_color, border_width):
		self.width = width
		self.height = height
		self.open_color = open_color # used to define base color
		self.set_color = set_color
		self.background_color = background_color
		self.border_width = border_width

# this class takes the settings and actually sets up where the buttons are and what they say
class Button:
	def __init__(self, x_pos = None, y_pos = None, button_settings = None, map_text = None, combat_text = None, action = None, text = None, pygame_key_id = None):
		# for readability, I'm going to move the settings from the settings object into this object
		self.button_settings = button_settings
		self.map_text = map_text
		self.combat_text = combat_text
		self.width = self.button_settings.width
		self.height = self.button_settings.height
		self.open_color = self.button_settings.open_color
		self.set_color = self.button_settings.set_color
		self.background_color = self.button_settings.background_color
		self.border_width = self.button_settings.border_width
		self.current_color = self.open_color
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.button_settings = button_settings # how big is it, what color is it, that stuff
		self.action = action # the function the button performs when it's pressed by the user
		self.pygame_key_id = pygame_key_id
		self.needs_to_be_updated = False
		self.status = "open" # "open" means it hasn't been pressed, "set" means it's been pressed, and will be used as the next command on submit
		
		if self.width is not None and self.height is not None and self.open_color is not None and self.background_color is not None and self.border_width is not None:
			self.button_surface = pygame.Surface((self.width,self.height))
			self.button_surface.fill(self.background_color)
			self.button_surface.fill(self.current_color,(self.border_width, self.border_width, self.width - 2* self.border_width, self.height - 2* self.border_width))

		if self.map_text is not None:
			# draw the text on the button
			self.button_text_image = Text_font.render(self.map_text,1,self.background_color)
			text_dimensions = Text_font.size(self.map_text)
			self.button_surface.blit(self.button_text_image,[self.width/2-text_dimensions[0]/2,self.height/2-text_dimensions[1]/2])
		main_screen.blit(self.button_surface,(self.x_pos,self.y_pos))

	def draw_self(self, combat_mode = 0, map_mode = 0):
		self.button_surface.fill(self.current_color,(self.border_width, self.border_width, self.width - 2* self.border_width, self.height - 2* self.border_width))

		if any([combat_mode, map_mode]):
			if combat_mode == 0:
				text_to_use = self.combat_text
			if map_mode == 0:
				text_to_use = self.map_text
			
			if text_to_use is not None:
				text_dimensions = Text_font.size(text_to_use)
				self.button_text_image = Text_font.render(text_to_use,1,self.background_color)
				self.button_surface.blit(self.button_text_image,[self.width/2-text_dimensions[0]/2,self.height/2-text_dimensions[1]/2])
		main_screen.blit(self.button_surface,(self.x_pos,self.y_pos))
		self.needs_to_be_updated = False
		
	def change_status(self, new_status):
		self.needs_to_be_updated = True
		if new_status == "set":
			self.status = "set"
			self.current_color = self.set_color
			for each_button in BUTTONS:
				if each_button.pygame_key_id is not self.pygame_key_id and each_button.status is "set":
					each_button.change_status(new_status = "open")
		elif new_status == "open":
			self.status = "open"
			self.current_color = self.open_color
		else:
			sys.exit("You tried to set a button to something it can't be.")
	def perform_action(self):
		z=1


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
		self.needs_to_be_updated = False
		
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
		# i want to change this so it's multifunctional. right now it's tied into the game state, but i want to make the draw_self method agnostic of what's actually going on in the game
		# the screen will take care of actually rendering text, you just have to point it to where the text is it needs to render
		
		# right now I have some confused functionality between preparing the image and putting the image on the main screen
		self.display_text(text_to_draw)
		self.needs_to_be_updated = False
		main_screen.blit(self.screen_image,(self.x_pos,self.y_pos))
		# check current story element
		# figure out which text to display
		# call display_text() and pass it the appropriate text
		
		# WARNING: right now this won't be able to display more text than the screen can handle, it will just cut it off.
		# put together a scroll widget that I can use to inform the screen of how to position the text


	
class Map:
	def __init__(self):
		# any attribute name you use here has to match how it will be written in the spec file
		self.Node_Name = None
		self.NPCs = None
		self.items = None
		self.effects = None # if you want to do something like, the room takes away five health per turn
		self.Story_Element_Names = None
		self.Flags = None
		self.Descriptive_Text = None

class StoryElement:
	def __init__(self, element_name, paths):
		self.element_name = element_name
		self.paths = paths # is a list of the names of the paths
		# the story element keeps track of the paths and their prerequisites
	def choose_path(self):
		# look at your stored story paths
		# if there's only one, then do the appropriate stuff: send the text to the screen, modify buttons, change game state, etc
		# if there's more than one, check the prerequisites for each
		x=1

		
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
	def move_character(self, new_location):
		x=1
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
def parse_node_file(filename, node_storage, type):
	file = open(filename)
	internal_check = 0
	if type is "map":
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
			print(current_line)
			if re.search("\]",line):
				name_search = re.search("\[(.+?):",current_line)
				if name_search is None:
					sys.exit("Your game file has no element name I can see")
				current_name = name_search.group(1)
				print("current name is "+str(current_name))
				content_search = re.search(":(.+?)\]",current_line)
				if content_search is None:
					sys.exit("Your game file has no element content I can see")
				current_text = content_search.group(1)
				print("current content is "+str(current_text))
				current_node.__setattr__(current_name, current_text)
				internal_check -= 1
			if re.search("}",line):
				node_storage.append(current_node)
				current_node = None
				internal_check -= 1
				if internal_check is not 0:
					sys.exit("Your game file has mismatched delimiters")
	elif type is "story":
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
			print(current_line)
			if re.search("\]",line):
				name_search = re.search("\[(.+?):",current_line)
				if name_search is None:
					sys.exit("Your game file has no element name I can see")
				current_name = name_search.group(1)
				print("current name is "+str(current_name))
				content_search = re.search(":(.+?)\]",current_line)
				if content_search is None:
					sys.exit("Your game file has no element content I can see")
				current_text = content_search.group(1)
				print("current content is "+str(current_text))
				current_node.__setattr__(current_name, current_text)
				internal_check -= 1
			if re.search("}",line):
				node_storage.append(current_node)
				current_node = None
				internal_check -= 1
				if internal_check is not 0:
					sys.exit("Your game file has mismatched delimiters")

# These are the settings for regular UI interaction buttons
direction_combat_button_settings = Settings(width=BUTTON_WIDTH, height = BUTTON_HEIGHT, open_color = BUTTON_OPEN_COLOR, set_color = BUTTON_SET_COLOR, background_color = BUTTON_BACKGROUND_COLOR, border_width = BUTTON_BORDER_WIDTH)

w_button = Button(x_pos = 255, y_pos = 362, button_settings = direction_combat_button_settings, map_text = "North", combat_text = "Heavy Attack", pygame_key_id = K_w)
a_button = Button(x_pos = 130, y_pos = 393, button_settings = direction_combat_button_settings, map_text = "West", combat_text = "Roll Left", pygame_key_id = K_a)
s_button = Button(x_pos = 255, y_pos = 393, button_settings = direction_combat_button_settings, map_text = "South", combat_text = "Light Attack", pygame_key_id = K_s)
d_button = Button(x_pos = 375, y_pos = 393, button_settings = direction_combat_button_settings, map_text = "East", combat_text = "Roll Right", pygame_key_id = K_d)
q_button = Button(x_pos = 130, y_pos = 362, button_settings = direction_combat_button_settings, map_text = "Examine", combat_text = "Block", pygame_key_id = K_q)
f_button = Button(x_pos = 500, y_pos = 393, button_settings = direction_combat_button_settings, map_text = "Commit", combat_text = "Commit", pygame_key_id = K_f)

BUTTONS.extend([w_button,a_button,s_button,d_button,q_button,f_button])
	
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

# the main loop just polls the keyboard for events
# it calls the appropriate button based on the key input
# it's agnostic to what the buttons actually do or what's being displayed on screen
# the buttons call handler functions that perform the proper actions mased on checking the combat_mode and map_mode flags

def combat_turn(all_combatants):
	# figures out initiative, performs combat
	if combat_mode == 0:
		return None
	elif combat_mode == 1 and player_ready == 1:
		combat_order = sorted(all_combatants,key = lambda x: x.calc_initiative_target(all_combatants)) # calc_initiative_target() chooses the target's initiative and target, this function sorts by initiative
		for each in combat_order:
			each.attack_action(each.target)
		
def map_turn(player,action, target=None):
	# map_turn() is the main non-combat function that controls the game.
	# this function will perform movement by changing game state and switching player position in the map node collection
	# it will also facilitate environment/npc interactions by invoking the story objects associated with the current map node
	if map_mode == 0:
		return None
	if action == "move":
		x=1
		#move player
	elif action == "examine" and target is None:
		x=1
		#examine the map node
	elif action == "examine" and target is not None:
		x=2
		#examine an object
	elif action == "inventory":
		x=2
		#open inventory menu
	
	if len(CURRENT_NODE) is not 0:
			text_to_draw = CURRENT_NODE[0].Descriptive_Text
	else:
		text_to_draw = "lol placeholder"
	Main_Inferface_Screen.draw_self(text_to_draw)

def process_turn(combat_mode, map_mode, player_action = None, ready_mode = 0):
	# ready_mode determines whether the player is ready for a game update
	# if the player is ready, process_turn() invokes map_turn(), which either looks at the current map node (if it's a non-movement action that needs to be performed) for text to display, or moves the player and then looks to the map node
	if combat_mode not in [0,1] or map_mode not in [0,1] or ready_mode not in [0,1] or combat_mode == map_mode:
		sys.exit("Your game control logic is faulty")
	
	if combat_mode is 1:
		x=1
		# get all present entities from the current map node
		# pass them to combat_turn
		
	if map_mode is 1 and ready_mode is 1:
		x=1
		# use player_action and the current map node to figure out what to do
	

def draw_whole_screen(combat_mode = 0, map_mode = 0):
	# right now this game structure is kind of fucked up, i should make it so that you just assume they dont need to be changed unless the user instructions tell you to modify it, which should happen before this step
	if combat_mode not in [0,1] or map_mode not in [0,1] or combat_mode == map_mode:
		sys.exit("Your game control logic is faulty")
	
	for each_button in BUTTONS:
		if each_button.needs_to_be_updated is True:
			each_button.draw_self(combat_mode, map_mode)
	for each_screen in SCREENS:
		if each_screen.needs_to_be_updated is True:
			each_screen.draw_self(combat_mode, map_mode)

Main_Interface_Screen = Screen([10,10,600,200], background_color=BUTTON_BACKGROUND_COLOR, foreground_color=BUTTON_OPEN_COLOR, text_color=[0,0,0], border_width=10)
Main_Interface_Screen.needs_to_be_updated = True
SCREENS.append(Main_Interface_Screen)

parse_node_file("map.txt",MAPS,type="map")
CURRENT_NODE.append(MAPS[0])
print(CURRENT_NODE[0].Descriptive_Text)

parse_node_file("story_elements.txt",STORY_ELEMENTS,type="story")

map_mode = 1
combat_mode = 0
ready_mode = 0
while exit_status is 0:
	next_event = pygame.event.poll()
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
	
	process_turn(combat_mode, map_mode)
	# process_turn() looks at the game state and decides what to do - in map mode, it asks the map node what text to display, then tells the screens to display that text, and in combat mode, it calls the functions that carry out combat
		
	draw_whole_screen(combat_mode,map_mode)
	pygame.display.flip() #flip updates the main_screen to the actual displayscreen

pygame.quit()
