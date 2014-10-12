#BEHOLD THE BLANK PAGE
import re, sys
import pygame
from pygame.locals import *
from settings import *
import random

# let's get the PyGame initialization out of the way
(numberpassed, numberfailed) = pygame.init()

print("initiating main screen")
main_screen = pygame.display.set_mode( [SCREEN_WIDTH, SCREEN_HEIGHT] )
exit_status = 0 # for quitting the main loop
center_box = pygame.Surface([SCREEN_WIDTH, SCREEN_HEIGHT])
center_box.fill([255,255,255])
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
UI_BUTTONS = [] # this is for invariant buttons like tab and confirm
OPTION_BUTTONS = [] # this is for variable-text option buttons
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
BUTTON_CONFIRM_SETTINGS[K_1] = "Press F to continue"

BUTTON_COMBAT_SETTINGS = {each:"" for each in [K_w,K_a,K_s,K_d,K_1,K_2,K_3,K_4,K_r,K_e,K_q]}
BUTTON_COMBAT_SETTINGS[K_f] = "Confirm"
BUTTON_COMBAT_SETTINGS[K_w] = "Strong Attack"
BUTTON_COMBAT_SETTINGS[K_s] = "Weak Attack"
BUTTON_COMBAT_SETTINGS[K_a] = "Roll Left"
BUTTON_COMBAT_SETTINGS[K_d] = "Roll Right"
BUTTON_COMBAT_SETTINGS[K_q] = "Block"

ALL_BUTTONS = []
ALL_BUTTONS.extend(OPTION_BUTTONS)
ALL_BUTTONS.extend(MOVEMENT_BUTTONS)

BUTTON_BLANK_OUT_ALL = {each:"" for each in ALL_BUTTONS}

def blank_all_buttons():
	for each_button in ALL_BUTTONS:
		each_button.set_text("")

def wait_for_confirm():
	print("going to wait for confirm")
	move_on_status = 0
	while move_on_status is 0:
		print("waiting")
		pygame.event.clear()
		next_event = pygame.event.wait()
		if next_event == pygame.NOEVENT:
			continue
		if next_event.type == KEYDOWN and next_event.key == K_f:
			print("confirm seen")
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
		self.action = ""
		
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

	def exec_action(self):
		if type(self.action) is list:
			for each_action in self.action:
				exec(each_action)
		elif type(self.action) is str:
			exec(self.action)


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
	
	def flavor_text(self, reference, value):
		# this function looks up the flavor text for a piece of text
		for each_flavor in FLAVOR_TEXT:
			if each_flavor.Attribute_Name == reference:
				text_to_use = each_flavor.bin_list[0][1]
				for each_bin in each_flavor.bin_list:
					if each_bin[0] <= value:
						text_to_use = each_bin[1]					
					elif each_bin[0] > value:
						break
				break
		return text_to_use

	def wrap_text(self, text, image_width):
		# take in text, return a list of wrapped text
		# TODO: MAKE IT BREAK THE LINE ON NEWLINE CHARACTERS
		#print("starting wrap_text")
		wrapped_text = []
		if self.check_length(text, image_width) is True:
			wrapped_text.append(text)
		string_front_half = ""
		string_back_half = text
		
		split_strings = string_back_half.split("====")
		for each_item in split_strings:	
			all_words = each_item.split(" ")
			temp_line = ""
			while len(all_words) > 0:
				current_word = all_words[0]
				temp_line += " " + current_word
				#print(temp_line)
				del(all_words[0])
				if self.check_length(temp_line, image_width) is False:
					#print("too long, going back a word")
					length_to_remove = len(current_word) + 1
					temp_line = temp_line[:-length_to_remove]
					all_words.insert(0,current_word)
					wrapped_text.append(temp_line)
					temp_line = ""
			wrapped_text.append(temp_line)		
		edited_list = []

		for each_item in wrapped_text:
			if type(each_item) is str and len(each_item)>1 and each_item[0] is " ":
				edited_list.append(each_item.lstrip())
			else:
				edited_list.append(each_item)

		return edited_list

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
		#split_line = re.split(
		lines_to_display = self.wrap_text(text,self.width - 4*self.border_width)
		print("printing "+str(len(lines_to_display))+" lines")
		#print(len(lines_to_display)*Text_font.get_linesize())

		if lines_to_display is not None: 
			print("replace mode is "+str(replace_mode))
			#print(type(replace_mode))
			if replace_mode == "True" or replace_mode is True: # replace the whole text image with a new one
				new_height = len(lines_to_display)*Text_font.get_linesize()
				#print(new_height)
				image_height = self.screen_image.get_height() - 2*self.border_width
				#print(image_height)
				if new_height > image_height:
					length_to_use = len(lines_to_display)*Text_font.get_linesize()
					#print("conditional worked")
				else:
					length_to_use = self.screen_image.get_height()-2*self.border_width
					#print("conditional failed")
				self.text_image = pygame.Surface([self.width - 2*self.border_width, length_to_use])
				#print("new height is "+str(self.text_image.get_height()))
				line_counter = 0
				for each_line in lines_to_display:
					#print(each_line)
					line_image = Text_font.render(each_line,1,self.background_color)
					self.text_image.blit(line_image, [Text_font.get_linesize(), Text_font.get_linesize() + line_counter * Text_font.get_linesize()])
					line_counter += 1

			elif replace_mode == "False" or replace_mode is False: # add the new text to the existing text image
				print("height is "+str(2*len(lines_to_display)*Text_font.get_linesize()))
				#print(self.screen_image.get_height())
				if len(lines_to_display)*Text_font.get_linesize() + self.text_image.get_height() > self.screen_image.get_height() - 2*self.border_width:
					length_to_use = self.screen_image.get_height() - 2*self.border_width
				else:
					length_to_use = len(lines_to_display)*Text_font.get_linesize() + self.text_image.get_height()
				temporary_surface = pygame.Surface([self.width - 2*self.border_width, length_to_use])
				temporary_surface.blit(source = self.text_image,dest=(0,0))
				line_counter = 0
				for each_line in lines_to_display:
					#print(each_line)
					line_image = Text_font.render(each_line,1,self.background_color)
					temporary_surface.blit(line_image,[Text_font.get_linesize(),self.text_image.get_height()+Text_font.get_linesize() + line_counter*Text_font.get_linesize()])
					line_counter += 1
				self.text_image = temporary_surface

			#print("text image height is "+str(self.text_image.get_height()))
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
			print("the string didn't ask for a confirm")
			self.display_text(text_to_draw,replace_mode=replace_mode)
			update_count += 1
			main_screen.blit(self.screen_image,(self.x_pos,self.y_pos))
			pygame.display.flip() #flip updates the main_screen to the actual displayscreen
			#if confirm_mode is True or confirm_mode == "True":
				#print("waiting for self as part of draw_self call")
				#wait_for_confirm()
		else:
			print("the string asked for a confirm")
			for each_segment in confirm_break_search:
				self.display_text(each_segment,replace_mode=replace_mode)
				update_count += 1
				main_screen.blit(self.screen_image,(self.x_pos,self.y_pos))
				pygame.display.flip() #flip updates the main_screen to the actual displayscreen
				if confirm_mode is True or confirm_mode == "True":
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
		self.screen_image.fill(self.background_color)
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
		self.Items = None # should be a list of actual objects, not just string names
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
		if self.Destinations is not "None" and self.Destinations is not None:
			self.Destinations = self.Destinations.split(",")
		if self.NPCs is not "None" and self.NPCs is not None:
			self.NPCs = self.NPCs.split(",")
		if self.Story_Element_Names is not "None" and self.Story_Element_Names is not None:
			self.Story_Element_Names = self.Story_Element_Names.split(",")
		if self.Flags is not "None" and self.Flags is not None:
			self.Flags = self.Flags.split(",")
			for each_flag in self.Flags:
				print(each_flag)
				if "=" in each_flag:
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
					if current_story is None:
						current_story = each_element
					
					print("adding story "+each_element.Node_Name)
		if current_story is not None:
			story_factors = []
			current_story_factors = current_story.get_story_text()
			if current_story_factors is not None: 
				print("found story factors, returning")
				print(current_story_factors)
				return current_story_factors
			else:
				return None
		print("returning default text")
		print(self.Descriptive_Text)
		return self.Descriptive_Text

	def query_story_info(self,name):
		print("a specific story was requested")
		current_story = None
		for each_element in STORY_ELEMENTS:
			if each_element.Node_Name == name:
				current_story = each_element
				print("found the story you want to add")
		if current_story is not None:
			print("returning the story info you requested")
			story_factors = current_story.get_story_text()
			if story_factors is not None and len(story_factors) is not 0:
				return story_factors
			else:
				print("can't return nothing")
				return None
			


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

		# ONLY RETURN ONE
		print("checking paths for "+self.Node_Name)
		paths_to_return = ""
		for each_path in self.Paths:
			story_flags_to_evaluate = getattr(self,each_path+"_Prerequisites") # should be a list
			if story_flags_to_evaluate is None:
				print("no story flags to check")
				return None
			path_results = []
			for each_flagset in story_flags_to_evaluate:
				flag_location, flag_test = each_flagset.split(",")
				if flag_test == "False":
					print("you hit a false start")
				if flag_test == "True":
					path_results.append(True)
					continue
				seen=0
				for each_node in MAPS:
					if each_node.Node_Name == flag_location:
						flag_search = re.search("(.+?)[=|<|>|!]",flag_test)
						flag_name = flag_search.groups(0)[0]
						actual_flag_value = getattr(each_node,flag_name) 
						print("map node to use is "+each_node.Node_Name)
						print("map flag name is "+str(flag_name))
						exec(flag_name+"="+actual_flag_value)
						result = eval(flag_test)
						path_results.append(result)
						seen = 1
				if seen == 0:
					result=eval(flag_test)
					path_results.append(result)
			if path_results is not []:
				if all(path_results) is True:
					print("this path is alright to use")
					paths_to_return = each_path
					break
		if paths_to_return is not "":
			return paths_to_return
		else:
			return None

	def get_story_text(self):
		# this is what you call when you want to get story text from the element
		story_to_use = self.choose_path() 
		story_info_to_return = []
		if story_to_use is None:
			return None
		print("story to use is "+str(story_to_use))
		if story_to_use is not None:
			text_to_display = getattr(self,story_to_use+"_Story_Content")
			effects_to_enact = getattr(self,story_to_use+"_Effects")
			buttons_to_display = getattr(self,story_to_use+"_Buttons")
			actions_to_set = getattr(self,story_to_use+"_Button_Effects")
			#print("type of actions is "+str(type(actions_to_set)))
			for each_key in buttons_to_display:
				if each_key in ["K_1","K_2","K_3","K_4"]:
					value = buttons_to_display[each_key]
					index = ["K_1","K_2","K_3","K_4"].index(each_key)
					new_buttons = [K_1,K_2,K_3,K_4]
					del buttons_to_display[each_key] 
					buttons_to_display[new_buttons[index]] = value
			for each_key in actions_to_set:
				if each_key in ["K_1","K_2","K_3","K_4"]:
					value = actions_to_set[each_key]
					index = ["K_1","K_2","K_3","K_4"].index(each_key)
					new_buttons = [K_1,K_2,K_3,K_4]
					del actions_to_set[each_key] 
					actions_to_set[new_buttons[index]] = value
			confirm_status = getattr(self,story_to_use+"_Confirm")
			replace_status = getattr(self,story_to_use+"_Replace")
			story_info_to_return = [text_to_display, effects_to_enact, buttons_to_display, confirm_status, replace_status, actions_to_set]
		if story_info_to_return is not []:
			return story_info_to_return
		else:
			return None
			
		# look at your stored story paths
		# if there's only one, then do the appropriate stuff: send the text to the screen, modify buttons, change game state, etc
		# if there's more than one, check the prerequisites for each

	def make_lists(self):
		if self.Paths is not "None" and self.Paths is not None:
			self.Paths = self.Paths.split(",")
		for each_attribute in dir(self):
			if re.search("Button",str(each_attribute), re.IGNORECASE):
				text_to_split = getattr(self,str(each_attribute))
				if text_to_split is "None":
					continue
				split_text = text_to_split.split(";")
				setattr(self,each_attribute,split_text)
				temp_dict = {}
				print(each_attribute)
				print(split_text)
				for each_item in split_text:
					[key_id,text] = each_item.split("|")
					temp_dict[key_id] = text
				if temp_dict is not {}:
					setattr(self,each_attribute,temp_dict)
		valueof = lambda x: getattr(self,each_pathname + x)
		if self.Paths is not "None" and self.Paths is not None:
			for each_pathname in self.Paths:
				string_to_split = valueof("_Prerequisites")
				prerequisite_list = string_to_split.split("|")
				setattr(self,each_pathname+"_Prerequisites",prerequisite_list)
				self.each_pathname = {"Story_Content":valueof("_Story_Content"), "Effects":valueof("_Effects"), "Buttons":valueof("_Buttons"),"Button Effects":valueof("_Button_Effects")}
		
class AI_settings:
	# this class will be used to set what the playstyles of the NPCs are	
	def __init__(self, Style = None):
		self.Style = Style # for example, some NPCs may be a caster type, and biased toward magic use
		self.owner = None
		# Style is a list of numbers which represent the extra weighting that character gives to that type
		# [[Physical_Attack, Spell_Attack], [Attack, Block, Dodge, Roll, Caution_Threshold]]
		# a 1 in physical or spell attack bumps up the corresponding value by 5% (2, 10%) of ITS OWN VALUE
		# if you have two attacks with the same damage, then you have equal probability of getting either one, so it'd be [1,1] for each

		# THIS IS A BAD SYSTEM
		# make it so it's an integer system, where teh number is how many shares it gets
		# like, if it's [3,5,6], there's 14 total shares, option 0 gets 3 of them, you choose randomly from the 14
		if self.Style is None:
			self.Style = [[0,0,0],[0,0,0,0,0]]
	
	def calculate_damage(self, item):
		weapon = self.owner.inventory[self.owner.inventory.index(item)]
		adjusting_stat = weapon.Governing_Stat
		owner_stat = getattr(self.owner, adjusting_stat)
		if type(weapon.Result) is not list:
			weapon.Result = weapon.Result.split("|")
		new_result_list = []
		for each_entry in weapon.Result:
			[attribute,value] = each_entry.split(",")
			if value in [str(each) for each in range(10)]:
				new_value = int(value) + owner_stat * 0.1 * int(value)
				new_result_list.append([attribute, new_value])
			else:
				new_result_list.append([attribute,value])
		return new_result_list

	def choose_attack__action(self):
		weapon_list = []
		for each_item in self.owner.inventory:
			if each_item.Type == "Weapon" or each_item.Type == "Spell":
				weapon_list.append(each_item)

		sorted_weapon_list = sorted(weapon_list,key = lambda item : self.calculate_damage(item))
		number_of_weapons = len(sorted_weapon_list)
		# 50% chance to choose something in the upper third of your weapon strengths
		# 40% chance to choose something in the middle third
		# 10% chance to choose something in the lower third
		
		# TODO: MAKE SURE THAT THIS DOESN'T BREAK IF THERE'S LESS THAN THREE ENTRIES IN THE LIST
		highest_value = self.calculate_damage(sorted_weapon_list[0])
		lowest_value = self.calculate_damage(sorted_weapon_list[-1])
		range_of_values = highest_value - lowest_value
		upper_third_cutoff = 0.67 * range_of_values + lowest_value
		lower_third_cutoff = 0.33 * range_of_values + lowest_value
		upper_third_identities = [self.calculate_damage(item) >= upper_third_cutoff for item in sorted_weapon_list]
		middle_third_identities = [self.calculate_damage(item) < upper_third_cutoff and self.calculate_damage(item) >= lower_third_cutoff for item in sorted_weapon_list]
		lower_third_identities = [self.calculate_damage(item) != True in upper_third_identities and self.calculate_damage(item) != True in middle_third_identities for item in sorted_weapon_list]
		if sum(upper_third_identities)+sum(lower_third_identities) + sum(middle_third_identities) != len(sorted_weapon_list):
			print("you messed up your conditionals")
		probability_dict = {}
		upper_prob = 0.5 / sum(upper_third_identities)
		middle_prob = 0.4 / sum(middle_third_identities)
		lower_prob = 0.1 / sum(lower_third_identities)
		for num in range(len(sorted_weapon_list)):
			if upper_third_identities[num] is True:
				probability_dict[sorted_weapon_list[num]] = upper_prob
			elif middle_third_identities[num] is True:
				probability_dict[sorted_weapon_list[num]] = middle_prob
			elif lower_third_identities[num] is True:
				probability_dict[sorted_weapon_list[num]] = lower_prob
		number_to_use = random.random()
		ref_number = 0
		weapon_to_use = None
		# TODO: MAKE IT ADD THE STYLE ADJUSTMENTS
		# ALSO: FIGURE OUT HOW I'M GOING TO DO THAT
		for each_key in probability_dict:
			ref_number += probability_dict[each_key]
			if ref_number >= number_to_use:
				weapon_to_use = each_key
		if weapon_to_use is not None:
			return weapon_to_use
		else:
			print("you couldn't choose a weapon")
			return None

	def choose_action(self, target):
		x=1
		# look at the target, evaluate what your most damaging moves would be from your possible moves
		# use possible damage to construct probability matrix for attacks
		# use inherent style biases to adjust probability matrix
		# choose, return
		attack_type_prefs = self.Style[1]

		# if you're damaged, decrease attack tendency
		#if

		# Style is a list of numbers which represent the extra weighting that character gives to that type
		# [[Physical_Attack, Spell_Attack], [Attack, Block, Dodge, Roll, Caution]]

class Item:
	def __init__(self, Node_Type = None, Node_Name = None, Descriptive_Text = None, Hit_Text = None, Miss_Text = None, Cost = None,Result = None, Uses = None, Durability = None, Recharge = None, Requirements = None, Governing_Stat = None):
		self.Node_Type = Node_Type
		self.Node_Name = Node_Name
		self.Descriptive_Text = Desctriptive_Text
		self.Hit_Text = Hit_Text
		self.Miss_Text = Miss_Text
		self.Cost = Cost
		self.Result = Result
		self.Uses = Uses
		self.Durability = Durability
		self.Recharge = Recharge
		self.Requirements = Requirements
		self.Governing_Stat = Governing_Stat
	
	def make_lists(self):
		x=1

class Character:
	# this class holds the information about where the NPCs are and what they're holding and how to move them
	def __init__(self, location, AI_component = None, name = None, Health = 1, Magic = 1, Stamina = 1, Strength = 1, Dexterity = 1, Resistance = 1, Intelligence = 1, Corruption = 1, Style = None):
		self.name = name
		self.location = location
		self.AI_component = AI_component
		self.target = None
		self.initiative = None
		self.character_image = None
		self.flavor_text = None # characters hold their own flavor text
		self.inventory = None # should be a list of actual objects, not strings

		# each stat represents a bonus that's added to the base damage of a weapon
		# for every point in a stat, you get an extra ten percent of damage with applicable weapon
		self.Health = Health
		self.Magic = Magic # resisted by intelligence
		self.Stamina = Stamina
		self.Strength = Strength # resisted by 2/3 resistance + 1/3 stamina
		self.Dexterity = Dexterity # resisted by 1/3 resistance + 2/3 stamina
		self.Resistance = Resistance
		self.Intelligence = Intelligence
		#self.Distortion = Distortion

		if self.AI_component is not None:
			self.AI_Component.owner = self

	def move_character(self, new_location):
		print("moving to "+str(new_location))
		global CURRENT_NODE
		current_node = None
		target_node = None
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
	def calc_initiative_vs_target(self, targets):
		z=1
		# calculate your initiative based on stats
		# choose target from possible targets
	def load_flavor_text(self):
		# go through flavor text file, add all flavor text that matches your character name to this object
		x=1
	
	def combat_action(self, target):
		x=1
		# this function decides what the character's action will be and examines the current character's stats and items
		# it returns the name of the attribute to change on the other character as well as the value to change it by
		# it will also perform self effects if necessary

		# return
		#[target, attack_text, hit, damage, attack_type, actions_effects] = Player.combat_action(first_npc)
		# attack_text is the text to display for what attack you made
		# hit is a True/False of whether the attack landed
		# actions_effects is a dict of the stat to change and the value to change it by
	
	def check_threshold(self, stat_value, challenge):
		if stat_value > 1.5 * challenge:
			return 0
		if stat_value > challenge:
			return 1
		if stat_value <= challenge:
			return round(challenge - stat_value)

	def receive_attack(self, attack_type = None, value = 0):
		# takes damage applied in combat, applies appropriate reductions based on stats, and then changes the health
		return_text = ""
		value_change = 0
		if attack_type is "physical_blunt":
			value_change = self.check_threshold(value, (1/3) * self.Resistance + (2/3) * self.Strength)
		elif attack_type is "magic":
			value_change = self.check_threshold(value, self.Intelligence)
		elif attack_type is "physical_thrust":
			value_change = self.check_threshold(value, (2/3) * self.Resistance + (1/3) * self.Strength)
		self.Health -= value_change
		return_text = "You take " + str(value_change) + " damage!"
		return return_text

	def change_attribute(self, name = None, value = 0):
		# this function changes an attribute
		# it will perform the appropriate checks to make sure you don't create a negative value or anything weird like that
		# if necessary, it will call the approrpiate death methods to remove the character from the game or end combat
		# this is a function like this so i don't have to deal with scoping issues
		attributes = dir(self)
		if name in attributes:
			old_value = getattr(self,name)
			if type(old_value) is not int:
				print("you tried to reference a stat that isn't an integer")
				return None
			setattr(self, name, getattr(self,name) + value)
			string_to_return = name + " is "
			if value > 0:
				string_to_return += "increased by " + str(value)
			elif getattr(self, name) < 0:
				setattr(self,name,0)
				string_to_return += "decreased by " + str(old_value)
			else:
				string_to_return += "decreased by " + str(value)
			return string_to_return
		else:
			return None
		
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
			if re.search("\]",line):
				name_search = re.search("\[(.+?):",current_line)
				if name_search is None:
					sys.exit("Your game file has no element name I can see")
				current_name = name_search.group(1)
				content_search = re.search(":(.+?)\]",current_line)
				if content_search is None:
					sys.exit("Your game file has no element content I can see")
				current_text = content_search.group(1)
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
		# actually i dont think thats true anymore
		Node_type = StoryElement
		current_line = ""
		# HOW AM I GOING TO STORE THE MULTIPLE PATH INFORMATION?
		# did i ever figure this out?
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
			if re.search("\]",line):
				name_search = re.search("\[(.+?):",current_line)
				if name_search is None:
					sys.exit("Your game file has no element name I can see")
				current_name = name_search.group(1)
				content_search = re.search(":(.+?)\]",current_line)
				if content_search is None:
					sys.exit("Your game file has no element content I can see")
				current_text = content_search.group(1)
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


w_button = Button(x_pos = 255, y_pos = 360, text = "North", button_settings = direction_combat_button_settings, pygame_key_id = K_w)
a_button = Button(x_pos = 130, y_pos = 390, text = "West", button_settings = direction_combat_button_settings, pygame_key_id = K_a)
s_button = Button(x_pos = 255, y_pos = 390, text = "South", button_settings = direction_combat_button_settings, pygame_key_id = K_s)
d_button = Button(x_pos = 380, y_pos = 390, text = "East", button_settings = direction_combat_button_settings, pygame_key_id = K_d)
q_button = Button(x_pos = 130, y_pos = 360, text = "Examine", button_settings = non_interactive_button_settings, pygame_key_id = K_q)
f_button = Button(x_pos = 505, y_pos = 390, text = "Confirm", button_settings = non_interactive_button_settings, pygame_key_id = K_f)
tab_button = Button(x_pos = 5, y_pos = 360, text = "Page", button_settings = non_interactive_button_settings, pygame_key_id = K_TAB)

opt_1 = Button(x_pos = 130, y_pos = 330, text = "Option 1", button_settings = non_interactive_button_settings, pygame_key_id = K_1)
opt_2 = Button(x_pos = 255, y_pos = 330, text = "Option 2", button_settings = non_interactive_button_settings, pygame_key_id = K_2)
opt_3 = Button(x_pos = 380, y_pos = 330, text = "Option 3", button_settings = non_interactive_button_settings, pygame_key_id = K_3)
opt_4 = Button(x_pos = 505, y_pos = 330, text = "Option 4", button_settings = non_interactive_button_settings, pygame_key_id = K_4)

MOVEMENT_BUTTONS.extend([w_button,a_button,s_button,d_button])
OPTION_BUTTONS.extend([opt_1, opt_2, opt_3, opt_4])
UI_BUTTONS.extend([f_button, tab_button, q_button])

print("setting up main text display")
Main_Interface_Screen = Screen([130,0,500,325], background_color=BUTTON_BACKGROUND_COLOR, foreground_color=BUTTON_OPEN_COLOR, text_color=[0,0,0], border_width=10)
SCREENS.append(Main_Interface_Screen)
	
# main strategy for game handling:
# when you first enter a node, check to see if there's hostile NPCs present
# if there are, set combat_mode=1
# while in combat mode, check to see if the timer flag is set, and what the time
# every loop, check the time and make sure you're under it.
# check for player input, and when you detect player input, start figuring out NPC combat actions
# apply actions, re-loop

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

	# THAT LIST THING I WAS DOING WAS DUMB, JUST GIVE IT AN INSERTION POINT

def set_up_all_buttons(dict_of_buttons_to_change):
	# this function takes a list of keys to change and the text they should be changed to, and changes them
	# it sets all other buttons to be greyed out
	# TODO: NO IT DOESN'T, STILL HAVE TO MAKE IT DO THAT
	# it expects a dict containing the button to change and the new text to assign to it
	global MOVEMENT_BUTTONS
	global OPTION_BUTTON
	global UI_BUTTONS
	print("buttons are "+str(dict_of_buttons_to_change))
	for each_button in MOVEMENT_BUTTONS:
		if each_button.pygame_key_id not in dict_of_buttons_to_change:
			each_button.set_text("")
	for each_button in OPTION_BUTTONS:
		if each_button.pygame_key_id not in dict_of_buttons_to_change:
			each_button.set_text("")
	for each_key in dict_of_buttons_to_change: # each_key is an integer, representing the key ID
		counter = 0
		for each_button in MOVEMENT_BUTTONS: # each_button is an object of the Button class
			if each_key == each_button.pygame_key_id:
				# i need the index in movement buttons of the object with id == key
				MOVEMENT_BUTTONS[counter].set_text(dict_of_buttons_to_change[each_key])
			counter += 1
		counter = 0
		for other_buttons in OPTION_BUTTONS:
			if each_key == other_buttons.pygame_key_id:
				print("setting "+str(other_buttons.pygame_key_id)+" to "+dict_of_buttons_to_change[each_key])
				OPTION_BUTTONS[counter].set_text(dict_of_buttons_to_change[each_key])
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

def assign_actions(list_of_actions):
	for each_button in OPTION_BUTTONS:
		if each_button.pygame_key_id in list_of_actions:
			each_button.action = list_of_actions[each_button.pygame_key_id]

def map_turn(player_action=None, target=None, ready_mode=0):
	# map_turn() is the main non-combat function that controls the game.
	# this function will perform movement by changing game state and switching player position in the map node collection
	# it will also facilitate environment/npc interactions by invoking the story objects associated with the current map node
	global update_count
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
				all_stories = None
				all_stories = [CURRENT_NODE[0].get_text()]
				if all_stories[0] == CURRENT_NODE[0].Descriptive_Text or type(all_stories[0]) is not list:
					text_to_draw = CURRENT_NODE[0].Descriptive_Text
					print("it's not a list")
					print("drawing the story")
					new_buttons = CURRENT_NODE[0].get_destinations()
					set_up_all_buttons(new_buttons)
					Main_Interface_Screen.draw_self(text_to_draw,confirm_mode=True,replace_mode=True)
					global update_count
					update_count += 1
					pygame.display.flip()
				elif all_stories is not None and type(all_stories[0]) is list:
					while len(all_stories) is not 0:
						print("the failing story is "+str(all_stories))
						newest_story = CURRENT_NODE[0].get_text() # it's returning a list in a list. WHY
						if newest_story not in all_stories and type(newest_story) is not str:
							all_stories.append(newest_story)
							print("you haven't already seen this one")
						current_story_info = all_stories.pop(0)
						print(current_story_info)
						if current_story_info is None:
							break
						text_to_draw = current_story_info[0]
						effects_to_enact = current_story_info[1]
						buttons_to_draw = current_story_info[2]
						confirm_status = current_story_info[3]
						replace_status = current_story_info[4]
						print(buttons_to_draw)
						set_up_all_buttons(buttons_to_draw)
						actions_to_set = current_story_info[5]
						assign_actions(actions_to_set)
						Main_Interface_Screen.draw_self(text_to_draw,replace_mode=replace_status,confirm_mode =confirm_status)
						pygame.display.flip()
						if effects_to_enact is not None:
							effects_list = effects_to_enact.split("|")
							for each_effect in effects_list:
								print(each_effect)
								[location,effect] = each_effect.split(",")
								attribute_set_search = re.search("(.+?),(.+?)=(.+)",each_effect)
								if attribute_set_search is not None:
									name = attribute_set_search.groups()[0]
									varname = attribute_set_search.groups()[1]
									value = attribute_set_search.groups()[2]
									for each_map in MAPS:
										if each_map.Node_Name == name:
											setattr(each_map, varname, value)
								if ">" in each_effect:
									print("there's an arrow sign")
									[effect_type_and_name,effect_name] = each_effect.split(">",1)
									[effect_location,effect_type] = effect_type_and_name.split(",")
									#if "insert_story" in effect_location:
									new_story_info = CURRENT_NODE[0].query_story_info(effect_name)
									print("story info is "+str(new_story_info))
									if new_story_info is not None:
										print("inserting story")
										all_stories.insert(0,new_story_info)
					# set all buttons to be blank except the Confirm button
						pygame.display.flip() #flip updates the main_screen to the actual displayscreen
						print("there are "+str(len(all_stories))+" stories left in the list")
						if confirm_status is True or confirm_status == "True":
							print("it asked to confirm, confirming")
							set_up_all_buttons(BUTTON_CONFIRM_SETTINGS)
							pygame.display.flip() #flip updates the main_screen to the actual displayscreen
							wait_for_confirm()
							if len(all_stories) < 1:
								default_dests = CURRENT_NODE[0].get_destinations()
								set_up_all_buttons(default_dests)
								text_to_draw = CURRENT_NODE[0].Descriptive_Text
								Main_Interface_Screen.draw_self(text_to_draw,replace_mode=True,confirm_mode=False)
								pygame.display.flip()
						elif len(all_stories) >= 1:
							print("there's more than one story, confirming before continuing")
							set_up_all_buttons(BUTTON_CONFIRM_SETTINGS)
							pygame.display.flip() #flip updates the main_screen to the actual displayscreen
							wait_for_confirm()
						else:
							print("only one story left, continuing then going back to normal")
							set_up_all_buttons(BUTTON_CONFIRM_SETTINGS)
							pygame.display.flip()
							wait_for_confirm()
							default_dests = CURRENT_NODE[0].get_destinations()
							set_up_all_buttons(default_dests)
							text_to_draw = CURRENT_NODE[0].Descriptive_Text
							Main_Interface_Screen.draw_self(text_to_draw,replace_mode=True,confirm_mode=False)
							pygame.display.flip()
					text_to_draw = CURRENT_NODE[0].Descriptive_Text
					Main_Interface_Screen.draw_self(text_to_draw,replace_mode=True,confirm_mode=False)
					new_buttons = CURRENT_NODE[0].get_destinations()
					print("using destination set as buttons")
					set_up_all_buttons(new_buttons)
					pygame.display.flip()
					
				else:
					text_to_draw = CURRENT_NODE[0].Descriptive_Text
					Main_Interface_Screen.draw_self(text_to_draw,replace_mode=True,confirm_mode=False)
					new_buttons = CURRENT_NODE[0].get_destinations()
					print("using destination set as buttons")
					set_up_all_buttons(new_buttons)
					pygame.display.flip()
			else:
				text_to_draw = CURRENT_NODE[0].Descriptive_Text
				Main_Interface_Screen.draw_self(text_to_draw,replace_mode=True,confirm_mode=False)
				new_buttons = CURRENT_NODE[0].get_destinations()
				print("using destination set as buttons")
				set_up_all_buttons(new_buttons)
				pygame.display.flip()
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

def combat_turn(player_action, target, ready_mode):
	global CURRENT_NODE
	set_up_all_buttons(BUTTON_COMBAT_SETTINGS)
	npc_initiative_dict = []
	CURRENT_NODE[0].NPCs.remove(Player)
	for each_npc in CURRENT_NODE[0].NPCs:
		each_npc.initiative = each_npc.calc_initiative_vs_target(Player)
	
	CURRENT_NODE[0].NPCs = sorted(CURRENT_NODE[0].NPCs, key = lambda npc: npc.initiative)	
	
	for each_npc in CURRENT_NODE[0].NPCs:
		Player.initiative = Player.calc_initiative_vs_target(each_npc)
		if each_npc.initiative <= Player.initiative: # give the player priority if the initiatives are equal
			CURRENT_NODE[0].NPCs.insert(CURRENT_NODE[0].NPCs.index(each_npc), Player)
			break
	if Player not in CURRENT_NODE[0].NPCs:
		CURRENT_NODE[0].NPCs.append(Player) # put them last since they never ended up in the list and they're the slowest
	
	# in the future, have the game ask the player which person they want to target
	# for now, assume the player is going to targe the first npc (satisfies the simplest case of two combatants)
	first_npc = None
	attacked = 0
	for each_npc in CURRENT_NODE[0].NPCs:
		if each_npc is not Player:
			[target, attack_text, hit, damage, attack_type, actions_effects] = each_npc.combat_action(Player) 
			if hit is True:
				combat_results = Player.receive_attack(attack_type = attack_type, value = damage)
			# hit is a True/False of whether the attack landed
		elif attacked is 0:
			[target, attack_text, hit, damage, attack_type, actions_effects] = Player.combat_action(first_npc)
			if hit is True:
				combat_results = target.receive_attack(attack_type = attack_type, value = damage)
			attacked = 1
		# look at the attack text, render it
		# look at the damage you actually did, render it
		# you add the returned text to the screen without replacing and without confirming

	#Main_Interface_Screen.draw_self(text_to_draw,replace_mode=False,confirm_mode=False)


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
		# pass them to cstatusombat_turn
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
	if new_action != action:
		ready_mode = 0
		action = new_action

while exit_status is 0:
	next_event = pygame.event.wait()
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
	
	# use t/g as small, v/b as large, y/h as full
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
	
	if next_event.type == KEYDOWN and next_event.key == K_1:
		opt_1.exec_action()
	if next_event.type == KEYDOWN and next_event.key == K_2:
		opt_2.exec_action()
	if next_event.type == KEYDOWN and next_event.key == K_3:
		opt_3.exec_action()
	if next_event.type == KEYDOWN and next_event.key == K_4:
		opt_4.exec_action()

	
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
