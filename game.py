#BEHOLD THE BLANK PAGE
import re, sys
import pygame
from pygame.locals import *
from settings import *

# let's get the PyGame initialization out of the way
(numberpassed, numberfailed) = pygame.init()

print("initiating main screen")
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
MAP_DISPLAY_KEYS = [K_w,K_a,K_s,K_d]
page_count = 0

# Start up the font object for text display
print("setting up font")
pygame.font.init()
Text_font = pygame.font.SysFont("C:\Windows\Fonts\04B_19_.TTF",FONT_SIZE)

BUTTON_CONFIRM_SETTINGS = {each:"" for each in [K_w,K_a,K_s,K_d,K_1,K_2,K_3,K_4,K_r,K_e,K_q]}
BUTTON_CONFIRM_SETTINGS[K_f] = "Continue"

ALL_BUTTONS = []
ALL_BUTTONS.extend(UI_BUTTONS)
ALL_BUTTONS.extend(MOVEMENT_BUTTONS)

def blank_all_buttons():
	for each_button in ALL_BUTTONS:
		each_button.set_text("")

def wait_for_confirm():
	move_on_status = 0
	while move_on_status is 0:
		next_event = pygame.event.poll()
		if next_event == pygame.NOEVENT:
			continue
		if next_event.type == KEYDOWN and next_event.key == K_f:
			move_on_status = 1

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
		global update_count
		update_count += 1
				

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
		main_screen.blit(self.screen_image,(self.x_pos,self.y_pos))
		self.text_image = None
		self.text_window_position = self.inner_dimensions
		
	def check_length(self, text, image_width):
		text_size = Text_font.size(text)
		text_width = text_size[0]
		if text_width > image_width:
			return False # text width greater than image width
		else:
			return True # text width less than image width

	def wrap_text(self, text, image_width):
		# take in text, return a list of wrapped text
		# TODO: MAKE IT BREAK THE LINE ON NEWLINE CHARACTERS
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
		
	def display_text(self, text, replace_mode=True):
		# this is the function you call when you want to tell a screen to display a piece of text
		# you don't call it directly, though, you tell the screen to use draw_self() and it looks at the current game state and the map node's story elements
		# mode is for whether you add or replace
		lines_to_display = None
		if text is None or text is "" or text is []:
			print("there's nothing to draw")
			return None
		lines_to_display = self.wrap_text(text,self.width - 4*self.border_width)
		print(len(lines_to_display)*Text_font.get_linesize())

		if lines_to_display is not None: 
			print("replace mode is "+str(replace_mode))
			print(type(replace_mode))
			if replace_mode == "True" or replace_mode is True: # replace the whole text image with a new one
				new_height = len(lines_to_display)*Text_font.get_linesize()
				print(new_height)
				image_height = self.screen_image.get_height() - 2*self.border_width
				print(image_height)
				if new_height > image_height:
					length_to_use = len(lines_to_display)*Text_font.get_linesize()
					print("conditional worked")
				else:
					length_to_use = self.screen_image.get_height()-2*self.border_width
					print("conditional failed")
				self.text_image = pygame.Surface([self.width - 2*self.border_width, length_to_use])
				print("new height is "+str(self.text_image.get_height()))
				line_counter = 0
				for each_line in lines_to_display:
					line_image = Text_font.render(each_line,1,self.background_color)
					self.text_image.blit(line_image, [Text_font.get_linesize(), Text_font.get_linesize() + line_counter * Text_font.get_linesize()])
					line_counter += 1

			elif replace_mode == "False" or replace_mode is False: # add the new text to the existing text image
				print("height is "+str(2*len(lines_to_display)*Text_font.get_linesize()))
				print(self.screen_image.get_height())
				if len(lines_to_display)*Text_font.get_linesize() + self.text_image.get_height() > self.screen_image.get_height() - 2*self.border_width:
					length_to_use = self.screen_,mage.get_height() - 2*self.border_width
				else:
					length_to_use = len(lines_to_display)*Text_font.get_linesize() + self.text_image.get_height()
				temporary_surface = pygame.Surface([self.width - 2*self.border_width, length_to_use])
				temporary_surface.blit(source = self.text_image,dest=(0,0))
				line_counter = 0
				for each_line in lines_to_display:
					line_image = Text_font.render(each_line,1,self.background_color)
					temporary_surface.blit(line_image,[Text_font.get_linesize(),self.text_image.get_height()+Text_font.get_linesize() + line_counter*Text_font.get_linesize()])
					line_counter += 1
				self.text_image = temporary_surface

			print(self.text_image.get_height())
			self.screen_image.fill(self.background_color)
			self.screen_image.fill(self.foreground_color, self.inner_dimensions_and_position)
			self.screen_image.blit(self.text_image,dest=self.inner_dimensions_and_position, area = self.text_window_position)
			global update_count
			update_count += 1
	

	def draw_self(self, text_to_draw,confirm_mode=False,replace_mode=False):
		# this takes text, renders it using internal functions, pastes it on the screen, and tells the game to update the screen
		# mode can be add or replace
		global update_count

		confirm_break_search = text_to_draw.split("****")
		# draw the text, then wait_for_confirm() before sending the next one
		if len(confirm_break_search) is 1:
			self.display_text(text_to_draw,replace_mode=replace_mode)
			update_count += 1
			main_screen.blit(self.screen_image,(self.x_pos,self.y_pos))
			pygame.display.flip() #flip updates the main_screen to the actual displayscreen
			if confirm_mode is True:
				wait_for_confirm()
		else:
			for each_segment in confirm_break_search:
				self.display_text(each_segment,replace_mode=replace_mode)
				update_count += 1
				main_screen.blit(self.screen_image,(self.x_pos,self.y_pos))
				pygame.display.flip() #flip updates the main_screen to the actual displayscreen
				if confirm_mode is True:
					wait_for_confirm()

	def scroll(self,direction, amount):
		# bli the text image using an altered area argument to the normal destination argument
		# adjust the position of the area up or down by a certain amount
		# amount should be either "small","large","full"
		# full is eqvuialent to a home/end command
		# short is a shorter move, like an arrow key hit
		# large is like a pageup/pagedown hit
		# use t/g as small, v/b as large, y/h as full?

		#self.inner_dimensions = [topleft x coord, topleft y coord, bottom right x coord, bottom right y coord]

		print("scrolling " + direction + " by amount " + amount)
		if amount == "small":
			# make this three line heights
			skip = 3*Text_font.get_linesize()
		elif amount == "large":
			# make this 80% of a full screen height
			skip = round(0.8*(self.text_window_position[3]-self.text_window_position[1]))
		elif amount == "full":
			# make this the full height of the text_image
			if direction == "down":
				skip = self.text_image.get_height() - self.text_window_position[3]
			elif direction == "up":
				skip = self.text_window_position[1]
		print(self.text_window_position)
		print("skip is "+str(skip))

		# clamp to lower image border (upper image coordinates)
		if self.text_window_position[3] + skip > self.text_image.get_height() and direction == "down":
			# if applying the skip puts the lower border out of bounds of the text image
			skip = self.text_image.get_height() - self.text_window_position[3]
			print("clamping to lower border")
		# clam to upper image border (lower image coordinates)
		if self.text_window_position[1] - skip < 0 and direction == "up":
			skip = self.text_window_position[1]
			print("clamping to upper border")

		if direction == "up":
			self.text_window_position[1] -= skip
			self.text_window_position[3] -= skip
		elif direction == "down":
			self.text_window_position[1] += skip
			self.text_window_position[3] += skip

		print("text window position is "+str(self.text_window_position))

		# now we actually move the text
		self.screen_image.fill(self.foreground_color)
		self.screen_image.blit(source=self.text_image,dest=self.inner_dimensions_and_position, area = self.text_window_position)

		global update_count
		update_count += 1
		main_screen.blit(self.screen_image,(self.x_pos,self.y_pos))
		pygame.display.flip()
	
class Map:
	def __init__(self):
		# any attribute name you use here has to match how it will be written in the spec file
		self.Node_Name = None
		self.NPCs = None # expected to be a list of strings if present
		self.Items = None
		self.effects = None # if you want something like, the room takes away five health per turn
		self.Flags = None
		self.Descriptive_Text = None
		self.Destinations = None # expected to be a list
		self.page_number = 0 # for deciding which destinations to display if you have too many
		self.Story_Element_Names = None
		self.Removed_Destinations = None

	def __eq__(self, target):
		if self.Node_Name == target:
			return True
		else:
			return False

	def make_lists(self):
		if self.Destinations is not None:
			self.Destinations = self.Destinations.split(",")
		if self.NPCs is not None:
			self.NPCs = self.NPCs.split(",")
		if self.Story_Element_Names is not None:
			self.Story_Element_Names = self.Story_Element_Names.split(",")
		if self.Flags is not None:
			self.Flags = self.Flags.split(",")
			for each_flag in self.Flags:
				print(each_flag)
				name,value = each_flag.split("=")
				setattr(self, name, value)
	
	def get_destinations(self):
		# since we can only display four directions at a time
		# but we may have more than four directions to display
		# we need to check how many directions we have and choose which ones to send
		if len(self.Destinations) <= len(MAP_DISPLAY_KEYS):
			names_to_return = self.Destinations
		else:
			start_point = 0 + self.page_number*len(MAP_DISPLAY_KEYS)
			end_point = len(MAP_DISPLAY_KEYS) + self.page_number*len(MAP_DISPLAY_KEYS)
			if end_point >= len(self.Destinations):
				end_point = len(self.Destinations)
			names_to_return = self.Destinations[start_point:end_point]
		while len(names_to_return) < len(MAP_DISPLAY_KEYS):
			names_to_return.append("")
		dict_to_return = {each:names_to_return[MAP_DISPLAY_KEYS.index(each)] for each in MAP_DISPLAY_KEYS}
		return dict_to_return

	def turn_destinations_page(self):
		if len(self.Destinations) > len(MAP_DISPLAY_KEYS):
			if len(self.Destinations) - self.page_number * len(MAP_DISPLAY_KEYS) > len(MAP_DISPLAY_KEYS):
				self.page_number += 1
			else:
				self.page_number = 0

	def get_text(self):
		if self.Story_Element_Names is None:
			print("there are no stories")
			return self.Descriptive_Text
		current_story = None
		for each_story in self.Story_Element_Names:
			for each_element in STORY_ELEMENTS:
				print("checking "+str(each_element.Node_Name) +" against "+each_story)
				if each_element.Node_Name == each_story:
					current_story = each_element
		if current_story is not None:
			story_factors = current_story.get_story_text()
			if story_factors is not None:
				print("found story factors, returning")
				#print(story_factors)
				return story_factors
		print("returning default text")
		return self.Descriptive_Text


class StoryElement:
	def __init__(self):
		self.Node_Name = None
		self.Paths = None # is a list of the names of the paths
		# the story element keeps track of the paths and their prerequisites
	def choose_path(self):
		# this is an internal function that looks at the story's content and chooses which branch
		#if len(self.Paths) is 1:
			#print("only one path")
			#return self.Paths[0]
		print("checking paths")
		for each_path in self.Paths:
			story_flags_to_evaluate = getattr(self,each_path+"_Prerequisites") # should be a list
			if story_flags_to_evaluate is None:
				print("no story flags to check")
				return None
			path_results = []
			for each_flagset in story_flags_to_evaluate:
				flag_location, flag_test = each_flagset.split(",")
				for each_node in MAPS:
					if each_node.Node_Name == flag_location:
						flag_search = re.search("(.+?)[=|<|>|!]",flag_test)
						flag_name = flag_search.groups(0)[0]
						actual_flag_value = getattr(each_node,flag_name) 
						print(flag_name)
						exec(flag_name+"="+actual_flag_value)
						result = eval(flag_test)
						path_results.append(result)
		if path_results is not None:
			if all(path_results) is True:
				return each_path
		return None

	def get_story_text(self):
		# this is what you call when you want to get story text from the element
		story_to_use = self.choose_path()
		print(story_to_use)
		if story_to_use is not None:
			text_to_display = getattr(self,story_to_use+"_Story_Content")
			effects_to_enact = getattr(self,story_to_use+"_Effects")
			buttons_to_display = getattr(self,story_to_use+"_Buttons")
			confirm_status = getattr(self,story_to_use+"_Confirm")
			replace_status = getattr(self,story_to_use+"_Replace")
			return [text_to_display, effects_to_enact, buttons_to_display, confirm_status,replace_status]
		else:
			return None
			
		# look at your stored story paths
		# if there's only one, then do the appropriate stuff: send the text to the screen, modify buttons, change game state, etc
		# if there's more than one, check the prerequisites for each

	def make_lists(self):
		if self.Paths is not None:
			self.Paths = self.Paths.split(",")
		for each_attribute in dir(self):
			if re.search("button",str(each_attribute), re.IGNORECASE):
				text_to_split = getattr(self,str(each_attribute))
				split_text = text_to_split.split(";")
				setattr(self,each_attribute,split_text)
				temp_dict = {}
				for each_item in split_text:
					[key_id,text] = each_item.split("|")
					temp_dict[key_id] = text
				if temp_dict is not {}:
					setattr(self,each_attribute,temp_dict)
		valueof = lambda x: getattr(self,each_pathname + x)
		if self.Paths is not None:
			for each_pathname in self.Paths:
				string_to_split = valueof("_Prerequisites")
				prerequisite_list = string_to_split.split("|")
				setattr(self,each_pathname+"_Prerequisites",prerequisite_list)
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
		print("moving to "+str(new_location))
		global CURRENT_NODE
		current_node = None
		taret_node = None
		destination_is_present = False
		for each_location in MAPS:
			if each_location.__eq__(self.location):
				current_node = each_location
			if each_location.__eq__(new_location):
				destination_is_present = True
		if destination_is_present is False:
			return None
		if new_location is not "":
			can_move = 0	
			for each_path in current_node.Destinations:
				if each_path == new_location:
					can_move = 1
			if can_move is not 0:
				self.location = new_location
				for each_location in MAPS:
					if each_location.Node_Name == new_location:
						each_location.NPCs.append(self.name)
						CURRENT_NODE[0] = each_location
					if each_location.Node_Name == self.location:
						current_node.NPCs.remove(self.name)
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
		for line in file:
			line = line.rstrip('\n')
			if re.search("{",line):
				current_node = Node_type()
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

print("setting up main text display")
Main_Interface_Screen = Screen([10,10,600,200], background_color=BUTTON_BACKGROUND_COLOR, foreground_color=BUTTON_OPEN_COLOR, text_color=[0,0,0], border_width=10)
SCREENS.append(Main_Interface_Screen)
	
# main strategy for game handling:
# when you first enter a node, check to see if there's hostile NPCs present
# if there are, set combat_mode=1
# while in combat mode, check to see if the timer flag is set, and what the time
# every loop, check the time and make sure you're under it.
# check for player input, and when you detect player input, start figuring out NPC combat actions
# apply actions, re-loop

# if there's not hostile NPCs, then enter map mode/
# when you enter map mode, check the current map node, and look at its stories
# find the youngest unlocked story element, display it (unless it has a display_once flag set)
# if there are none, default to the basic node description

# it calls the appropriate button based on the key input
# it's agnostic to what the buttons actually do or what's being displayed on screen
# the buttons call handler functions that perform the proper actions mased on checking the combat_mode and map_mode flags

def remove_map_path(map_name, path_to_remove):
	# this function is for use in story element effects
	# it lets you remove the exits from a map node, for instance if you're locked in a dungeon or a tunnel collapsed
	for each_node in MAPS:
		if each_node.Node_Name is map_name:
			each_Node.Removed_Destinations = [0 for each in range(each_node.Destinations.index(path_to_remove))]
			each_Node.Removed_Destinations[each_node.Destinations.index(path_to_remove)] = path_to_remove
			each_Node.Destinations[each_Node.Destinations.index(path_to_remove)] = ""
			break

def add_map_path(map_name, path_to_add, insertion_point = None):
	# adds a path to the Destinations list
	# if you give it something that's never been there before,
	# if you give it a single string, add it to the end of the list
	# if you give it a list of form [False, False, False, False, path_to_add], it inserts at that location
	# if you give it something it's had before, it looks at Removed_Destinations and adds it back in in the same location
	for each_node in MAPS:
		if each_node.Node_Name is map_name:
			if each_node.Removed_Destinations is not None and path_to_add in each_node.Removed_Destinations:
				x=1
	# insertion point lets you add to a specific location where there is a None pathway leaving a Map Node
				

def set_up_all_buttons(dict_of_buttons_to_change):
	# this function takes a list of keys to change and the text they should be changed to, and changes them
	# it sets all other buttons to be greyed out
	# it expects a dict containing the button to change and the new text to assign to it
	global MOVEMENT_BUTTONS
	global UI_BUTTONS
	for each_key in dict_of_buttons_to_change: # each_key is an integer, representing the key ID
		counter = 0
		for each_button in MOVEMENT_BUTTONS: # each_button is an object of the Button class
			if each_key == each_button.pygame_key_id:
				# i need the index in movement buttons of the object wiht id == key
				MOVEMENT_BUTTONS[counter].set_text(dict_of_buttons_to_change[each_key])
			counter += 1
	global update_count
	update_count += 1
	pygame.display.flip()

def change_dest_names(list_to_modify):
	new_list = {}
	for each in list_to_modify.keys():
		if each is K_w:
			new_name = "move_up"
		elif each is K_a:
			new_name = "move_left"
		elif each is K_s:
			new_name = "move_down"
		elif each is K_d:
			new_name = "move_right"
		else:
			sys.exit("That's not a direction")
		value = list_to_modify[each]
		new_list[new_name] = value
	return new_list



def map_turn(player_action=None, target=None, ready_mode=0):
	# map_turn() is the main non-combat function that controls the game.
	# this function will perform movement by changing game state and switching player position in the map node collection
	# it will also facilitate environment/npc interactions by invoking the story objects associated with the current map node
	if ready_mode is 0 and player_action is not "change page":
		return None
	if player_action is not None:
		print(action)
	if map_mode == 0:
		return None
	possible_directions = ["move_up","move_left","move_down","move_right"] 
	if player_action in possible_directions:
		current_destinations = CURRENT_NODE[0].get_destinations() # returns a dict of keyname/destname
		print(current_destinations)
		CURRENT_NODE[0].page_number = 0 # clean up the paging before you leave
		#move player
		renamed_dests = change_dest_names(current_destinations)

		Player.move_character(renamed_dests[player_action])
	
		if len(CURRENT_NODE) is not 0: # ask the map what story elements it has, ask for a story
			if CURRENT_NODE[0].Story_Element_Names is not None:
				current_story_info = CURRENT_NODE[0].get_text()
				print(len(current_story_info))
				print(type(current_story_info))
				if type(current_story_info) is not list:
					text_to_draw = CURRENT_NODE[0].Descriptive_Text

					Main_Interface_Screen.draw_self(text_to_draw,confirm_mode=False,replace_mode=True)
				else:
					text_to_draw = current_story_info[0]
					effects_to_enact = current_story_info[1]
					buttons_to_draw = current_story_info[2]
					confirm_status = current_story_info[3]
					replace_status = current_story_info[4]
					set_up_all_buttons(buttons_to_draw)
					Main_Interface_Screen.draw_self(text_to_draw,replace_mode=replace_status,confirm_mode =confirm_status)
					if effects_to_enact is not None:
						effects_list = effects_to_enact.split(";")
						for each_effect in effects_list:
							attribute_set_search = re.search("(.+?),(.+?)=(.+)",each_effect)
							if attribute_set_search is not None:
								name = attribute_set_search.groups()[0]
								varname = attribute_set_search.groups()[1]
								value = attribute_set_search.groups()[2]
								for each_map in MAPS:
									if each_map.Node_Name == name:
										setattr(each_map, varname, value)
							if "(" in each_effect:
								exec(each_effect)
					# set all buttons to be blank except the Confirm button
					pygame.display.flip() #flip updates the main_screen to the actual displayscreen
					if confirm_status is True:
						set_up_all_buttons(BUTTON_CONFIRM_SETTINGS)
						pygame.display.flip() #flip updates the main_screen to the actual displayscreen
						wait_for_confirm()
				
			else:
				text_to_draw = CURRENT_NODE[0].Descriptive_Text
				Main_Interface_Screen.draw_self(text_to_draw,replace_mode=True,confirm_status=False)
			new_buttons = CURRENT_NODE[0].get_destinations()
			set_up_all_buttons(new_buttons)
		else:
			text_to_draw = "lol placeholder"
	elif player_action == "examine" and target is None:
		x=1
		#examine the map node
	elif player_action == "examine" and target is not None:
		x=2
		#examine an object
	elif player_action == "inventory":
		x=2
		#open inventory menu
	elif player_action == "change page":
		print("changing page")
		CURRENT_NODE[0].turn_destinations_page()	
		new_placenames = CURRENT_NODE[0].get_destinations()
		set_up_all_buttons(new_placenames)
		# TO DO LATER:  have it change the buttons to be "open"

	# figure out what buttons to draw

	#Main_Interface_Screen.draw_self(text_to_draw) # this doesn't belong here yet, it's not appropriate

def process_turn(combat_mode, map_mode, player_action = None, target = None, ready_mode =0):
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
	elif map_mode is 1 :
		map_turn(player_action, target,ready_mode=ready_mode)




Player = Character(name = "Player", location = None)

confirm_mode = False
replace_mode = True
print("parsing map file")
parse_node_file("map.txt",MAPS,node_type="map")
for each_map_node in MAPS:
	if "Player" in each_map_node.NPCs:
		CURRENT_NODE[0] = each_map_node
		Player.location = CURRENT_NODE[0].Node_Name
		Main_Interface_Screen.draw_self(each_map_node.Descriptive_Text,confirm_mode=confirm_mode,replace_mode=replace_mode)

if CURRENT_NODE[0] is None:
	sys.exit("You never defined a starting place for the player")

print("parsing story file")
parse_node_file("story_elements.txt",STORY_ELEMENTS,node_type="story")

print("setting up initial buttons")
starting_dests = CURRENT_NODE[0].get_destinations()
set_up_all_buttons(starting_dests)

map_mode = 1
combat_mode = 0
ready_mode = 1
target = None
action = None
print("starting main game loop")
def action_set(new_action):
	# so you don't have a confirm hanging around for the next time you hit a button
	global ready_mode
	global action
	#ready_search = re.compile('action.=."(\D.+?)"')
	if new_action != action:
		ready_mode = 0
		action = new_action

while exit_status is 0:
	next_event = pygame.event.poll()
	target = None
	if next_event == pygame.NOEVENT:
		continue
	if next_event.type == KEYDOWN and next_event.key == K_ESCAPE:
		exit_status = 1
	if next_event.type == KEYDOWN and next_event.key == K_w:
		w_button.change_status("set")
		if map_mode == 1:
			action_set("move_up")
		elif combat_mode == 1:
			action_set("light_attack")
	if next_event.type == KEYDOWN and next_event.key == K_a:
		a_button.change_status("set")
		action_set("move_left")
	if next_event.type == KEYDOWN and next_event.key == K_s:
		s_button.change_status("set")
		if map_mode == 1:
			action_set("move_down")
		elif combat_mode == 1:
			action_set("heavy_attack")
	if next_event.type == KEYDOWN and next_event.key == K_d:
		d_button.change_status("set")
		action_set("move_right")
	if next_event.type == KEYDOWN and next_event.key == K_q and combat_mode == 1:
		q_button.change_status("set")
		action_set("block")
	if next_event.type == KEYDOWN and next_event.key == K_e and combat_mode == 1:
		e_button.change_status("set")
		action_set("parry")
	
	# use t/g as small, v/b as large, y/h as full?
	if next_event.type == KEYDOWN and next_event.key == K_t :
		Main_Interface_Screen.scroll(direction = "up", amount = "small")
	elif next_event.type == KEYDOWN and next_event.key == K_g :
		Main_Interface_Screen.scroll(direction = "down", amount = "small")
	elif next_event.type == KEYDOWN and next_event.key == K_v :
		Main_Interface_Screen.scroll(direction = "up", amount = "large")
	elif next_event.type == KEYDOWN and next_event.key == K_b :
		Main_Interface_Screen.scroll(direction = "down", amount = "large")
	elif next_event.type == KEYDOWN and next_event.key == K_y :
		Main_Interface_Screen.scroll(direction = "up", amount = "full")
	elif next_event.type == KEYDOWN and next_event.key == K_h :
		Main_Interface_Screen.scroll(direction = "down", amount = "full")
		
	if next_event.type == KEYDOWN and next_event.key == K_x:
		action_set("examine_node")
		# pop up menu to choose target
		# call .get_most_recent_story(current_node) on the node
	
	if next_event.type == KEYDOWN and next_event.key == K_z:
		action_set("examine")
		# pull up the menu to choose an item
	
	if next_event.type == KEYDOWN and next_event.key == K_TAB:
		print("tab seen")
		action_set("change page")
		# pull up the menu to choose an item

	if next_event.type == KEYDOWN and next_event.key == K_f:
		print("confirm seen")
		ready_mode = 1
	
	if (action is not None and ready_mode is 1):
		process_turn(combat_mode = combat_mode, map_mode = map_mode, player_action=action, target = target, ready_mode = ready_mode)
		action = None
	elif action is "change page":
		process_turn(combat_mode = combat_mode, map_mode = map_mode, player_action=action, target = target, ready_mode =1)
		action = None
		
	# process_turn() looks at the game state and decides what to do
		
	if update_count is not 0:
		pygame.display.flip() #flip updates the main_screen to the actual displayscreen
		update_count = 0
		ready_mode = 0

pygame.quit()
