##############################################
# written by Joseph Farah on April 21, 2017
# Last updated July 27th 2017
##############################################

##############################################
#imports
##############################################

# consider adding try/except for pillow
import PIL.Image
from PIL import ImageDraw 
from PIL import ImageTk
import os
import random
import datetime
import time
import matplotlib.pyplot as plt
from Tkinter import *
from tkFileDialog import askopenfilename as selectFILE
import tkMessageBox as tkmb
# not necessary for the historical program because only this one downloads crap from the internet 
# scrap that its necessary for both, im an idiot
import shutil
import urllib
import sys
import re
import urllib2
from BeautifulSoup import BeautifulSoup as soup
import ssl
import requests

plt.style.use('classic')

##############################################
# count vars, global 
##############################################


# color and temperature ranges
no_stress_color_range = '#c8fafa'
watch_color_range = '#fff000'
warning_color_range = "#faaa0a"
alert_1_color_range = "#f00000"
alert_2_color_range = "#960000"
black_color_range = "#000000"
land_range = "#c8c8c8"

# temp colors
negativetwo = "#500014"
zero = "#500046"
five = "#280096"
ten = "#000096"
fifteen = "#0075ff"
twenty = "#00fc00"
twentyfive = "#e6fa00"
thirty = "#e6fa00"
thirtyfive = "#730000"

# count vars for percentages
no_stress = 0.0
watch_color = 0.0
warning_color = 0.0
alert_1_color = 0.0
alert_2_color = 0.0
black = 0.0
land = 0.0

# lists that need predefinition, including x/y datasets, 
# percentage points, etc
dataset = []
x_values = []
no_stress_points = []
watch_data_points = []
warning_data_points = []
alert_1_data_points = []
alert_2_data_points = []

# database file, will be dynamic so that users can update 
# with their own data file
database_file = os.path.normpath(r"C:\Users\Joseph Farah\Documents\python\coral\db\realtime.db")

# arg variable, will be filled if unknown arg is called
unknown_arg = ''

# variable for the continuous scan, is used by two
# functions so must be global and declared before hand
keepgoing = 0

# number of pH iterations
num_iter = 0

class fragile(object):
    class Break(Exception):
      """Break out of the with statement"""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error

class element_input:
    def __init__(self, parent, CONSTANT):

        top = self.top = Toplevel(parent)
        Label(top, text="Please enter how many times you want pH_collect to run").pack()

        self.e = Entry(top)
        self.e.pack(padx=5)

        b = Button(top, text="submit", command=self.enter_element)
        b.pack(pady=5)

    def enter_element(self):
    	global iterations
        new_value = self.e.get()
        iterations = int(new_value)

        self.top.destroy()

# defining the tkinter window
main = Tk()







##############################################
# FUNCTION DEFINITIONS, ABANDON ALL HOPE HE 
# WHO ENTERS HERE
##############################################
def get_pixel_color(image_object, x,y):
	'''gets the color at a specificed pixel
	arguments: image object (predefined), x and y coordinates of pixel
	returns: red green and blue, to be converted with convert_RGB_HEX'''
	rgb_im = image_object.convert('RGB')
	r, g, b = rgb_im.getpixel((x, y))

	return r,g,b

def get_image_size(image_object):
	'''gets the size of any of the various image objects'''
	return image_object.size

def clamp(random_var_name_1):
	'''needed for the conversion from RGB to HEX'''
  	return max(0, min(random_var_name_1, 255))

def convert_RGB_HEX(color_tuple):
	'''converts RGB values to HEX. Uses some magic I found on Stack Overflow'''
	return "#{0:02x}{1:02x}{2:02x}".format(clamp(color_tuple[0]), clamp(color_tuple[1]), clamp(color_tuple[2]))

def count_pixels(im):
	'''counts pixels in stress map and adds various color counts to various global variables'''
	# globalizing all needed variables
	global no_stress_color_range, watch_color_range, warning_color_range, alert_1_color_range, alert_2_color_range, no_stress, watch_color, warning_color, alert_1_color, alert_2_color, black_color_range, black, land_range, land
	# gets the image length and width, stores as vars within tuple
	(length, width) = get_image_size(im)
	# initiliazes pixels to zero, MUST BE DONE BEFORE USING THE FUNCTION
	pixels = 0
	# begins looping through every pixel in the image, checking for color
	for l in range(length):
		# this range is ONLY for testing purposes, will be replaced with "width"
		for w in range(181,182): 
			# grabs pixel color and converts it
			color = get_pixel_color(im, l, w)
			color = convert_RGB_HEX(color)
			# checks color of pixel against predefined ranges
			if color == no_stress_color_range:
				no_stress += 1
				pixels += 1
				continue
			elif color == watch_color_range:
				watch_color += 1
				pixels += 1
				continue
			elif color ==  warning_color_range:
				warning_color += 1
				pixels += 1
				continue
			elif color == alert_1_color_range:
				alert_1_color += 1
				pixels += 1
				continue
			elif color == alert_2_color_range:
				alert_2_color += 1
				pixels += 1
				continue
			elif color == black_color_range:
				black += 1
				pixels += 1
				continue
			elif color == land_range:
				land += 1
				pixels += 1
				continue
	# returns the number of pixels
	return pixels

def find_difference(list1, list2):
	'''given two lists, return a third list that removes all the elements from list 2 that exist in list 1'''
	previous_list = list1
	append_list = list2
	for new_element in list2:
		comp1 = new_element[-1]
		for old_element in list1:
			comp2 = old_element[-1]
			if comp2 == comp1:
				del append_list[list2.index(old_element)]
	return previous_list + append_list


def get_climate_change_statistics():
	url = "https://climate.nasa.gov"
	context = ssl._create_unverified_context()
	gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
	web_soup = soup(requests.get(url, verify=False).text)

	l = []

	# get main-content div
	main_div = web_soup.findAll(name="div", attrs={'class': 'change_number'})
	for element in main_div:
		print element
		l.append(float(str(element)[27:-7]))

	return l

def get_percentages(im, num, db_file):
	'''Does the math work of getting the percentages of each pixel color and writing them to the data file'''
	# globalizing all variables needed
	global no_stress_color_range, watch_color_range, warning_color_range, alert_1_color_range, alert_2_color_range, no_stress, watch_color, warning_color, alert_1_color, alert_2_color, black_color_range, black, land_range, land, database_file, bleaching_database_view
	database_file = db_file
	# sets all counter variables to zero in preparation for count_pixels, this MUST BE DONE BEFOREHAND
	no_stress, watch_color, warning_color, alert_1_color, alert_2_color = 0,0,0,0,0
	# floats the number of pixels returned so it can be used in the percentage count
	pixels  = float(count_pixels(im))
	# the values in the database will go in order of the alert levels, with a timestamp at the beginning delimited by a | DEPRECATED IGNORE THIS
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	program_print("GETTING PERCENTAGES")
	program_print("GETTING DATE TIME")
	# gets the date and time that the map was used by examining today's date and the placement of the gif entry in the file
	st = get_date(datetime.date.today(), 19+(27-int(num)))
	day_number = str(datetime.datetime.now().timetuple().tm_yday) + '.' + str(datetime.datetime.now().year)
	day_number = float(day_number)-(19+(27-int(num)))
	program_print(ts)
	# preps to add everything to the database by sticking it in a list first
	database_input_list = [st, no_stress/pixels, watch_color/pixels, warning_color/pixels, alert_1_color/pixels, alert_2_color/pixels, day_number]
	# im not even sure what this does, but do i want to risk taking it away?
	for element in database_input_list:
		if database_input_list.index(element) == 0:
			continue
		database_input_list[database_input_list.index(element)] == element
	# concatenates each line into a string 
	database_input = "".join(str(database_input_list))
	# opens the database file and sticks it in there
	with open(database_file, "r") as database:
		dataset = []
		data = []
		tmp_id_nums = []
		# read it into a list, each new line is a new entry
		data = database.read().splitlines()
		for d1 in data:
			# get rid of the brackets and the commas
			tmp = d1.strip('[]')
			dataset.append([d.strip() for d in tmp.split(',')])
		for element in dataset:
			tmp_id_nums.append(element[-1])

	with fragile(open(os.path.normpath(database_file), "a")) as database:
		# print database_input_list[-1]
		print tmp_id_nums
		if str(database_input_list[-1]) in tmp_id_nums:
			raise fragile.Break
		database.write(database_input+'\n')	
		# reads the data back out in preparation for the graph making
	with open(database_file, "r") as database:
		bleaching_database_view.delete('1.0', END)
		info_tmp = database.read()
		bleaching_database_view.insert(INSERT, info_tmp)

def generate_graphs(database_file):
	'''generates the graphs at request, using matplotlib, displays changing bleaching patterns over the last 30 days'''
	# globalizes all necessary variables
	global dataset, x_values, no_stress, watch_data_points, warning_data_points, alert_1_data_points, alert_2_data_points
	# initiliazes all the lists that will eventually be used as point holders on the graph
	data = []
	dataset = []
	no_stress_points = []
	watch_data_points = []
	warning_data_points = []
	alert_1_data_points = []
	alert_2_data_points = []
	x_values = []
	x_values_num = []
	# open the database file and read in the data
	with open(database_file, "r") as database:
		# read it into a list, each new line is a new entry
		data = database.read().splitlines()
		for d1 in data:
			# get rid of the brackets and the commas
			tmp = d1.strip('[]')
			dataset.append([d.strip() for d in tmp.split(',')])
		for element in dataset:
			# append all corresponding points to their home lists
			no_stress_points.append(float(element[1]))
			watch_data_points.append(float(element[2]))
			warning_data_points.append(float(element[3]))
			alert_1_data_points.append(float(element[4]))
			alert_2_data_points.append(float(element[5]))
		for t in range(len(no_stress_points)):
			# takes the number of days and makes a corresponding x value list for graphing
			x_values.append(str(dataset[t][0]))
			x_values_num.append(t)

	# defins the figure and axes
	fig, ax = plt.subplots(1,1)
	# sets the background color
	# ax.set_axis_bgcolor((0, 0, 0))
	# labels and plots all of the various data sets
	ax.plot(x_values_num, watch_data_points, color="yellow", label = 'WATCH')
	ax.plot(x_values_num, warning_data_points, color="orange", label = 'WARNING')
	ax.plot(x_values_num, alert_1_data_points, color="red", label = 'ALERT 1')
	ax.plot(x_values_num, alert_2_data_points, color="maroon", label = 'ALERT 2')
	# adds the labels
	plt.xlabel('Days since the first measurement in the dataset {0}'.format(str(dataset[0][0])))
	plt.ylabel('Percentage of reef at various alert levels')
	# creates the legend
	legend = ax.legend(loc='upper right', shadow=True)
	for label in legend.get_texts():
		label.set_fontsize('small')
	#displays the plot
	plt.show()

def analyze_images():
	'''downloads images from the NOAA and prepares them using standard ImageObjects for analysis'''
	download_current_image("https://coralreefwatch.noaa.gov/satellite/bleaching5km/images_current/cur_b05kmnn_max_r07d_baa_45ns.gif", "C:\Users\Joseph Farah\Documents\python\coral\db\current_frame.png")
	download_current_image("https://coralreefwatch.noaa.gov/satellite/bleaching5km/index_5km_dhw.php", "C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_temp.png")
	file_path = os.path.normpath("C:\Users\Joseph Farah\Documents\python\coral\db\current_frame.png")
	imageObject = PIL.Image.open(file_path) #Can be many different formats.
	# gets the percentages for each entry in the gif (last 30 days, so technically historical)
	get_percentages(imageObject, 1, os.path.normpath(r"C:\Users\Joseph Farah\Documents\python\coral\db\realtime.db"))
	tkmb.showinfo("Process Completed","Process complete, GRAPH ready to be GENERATED")

def analyze_cumulative():
	download_current_image("https://coralreefwatch.noaa.gov/satellite/bleaching5km/images_current_composite/cur_b05kmnn_baa_max_45ns.gif", 
							"C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_cumulative.png")
	im = PIL.Image.open("C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_cumulative.png")
	file_path = os.path.normpath("C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_cumulative.png")
	imageObject = PIL.Image.open(file_path)
	get_percentages(imageObject, 1, os.path.normpath(r"C:\Users\Joseph Farah\Documents\python\coral\db\realtime_cumulative.db"))
	tkmb.showinfo("Process complete", "Added cumulative data to relevant databases")

def download_current_image(url_link, path_to_save):
	'''function to download image, just makes it overall more readable'''
	urllib.urlretrieve(url_link, path_to_save)
	program_print('Image retrieved')

def get_database():
	'''featureset that is soon to be implemented, will allow user to select their own datafile for use'''
	global database_file
	databse_file = selectFILE()
	tkmb.showinfo("File Selected","DATABASE FILE SELECTED")	

def save_graph():
	'''test function'''
	print 'test'

def startup_function():
	'''the functiont that has to run as soon as the program starts up. loads all images, quickly loads databases for later reading, and displays some startup text to the user'''
	global unknown_arg
	NUM_BUTTONS_RIGHT_COLUMN = 5
	# opens and loads the database file into the corresponding tkinter window
	with open(database_file, "r") as database:
		bleaching_database_view.delete('1.0', END)
		info_tmp = database.read()
		bleaching_database_view.insert(INSERT, info_tmp)	
	# opens and loads startup text file into the corresponding tkinter window
	with open("startuptext.txt", "r") as info:
		program_ouput.delete('1.0', END)
		info_tmp = info.read()
		program_ouput.insert(INSERT, info_tmp)	
	
	# downloads current relevant statistics and places them into the window
	current_stats = get_climate_change_statistics()
	print current_stats
	Label(main, text = 'Global Carbon Dioxide (ppm): {0}'.format(current_stats[0])).grid(row = 0,column = 2)
	Label(main, text = 'Global temperature increase since 1880 (degrees F): {0}'.format(current_stats[1])).grid(row = 0,column = 3)
	Label(main, text = 'Imcrease in sea level (yearly, mm): {0}'.format(current_stats[4])).grid(row = 0,column = 4)

	# downloads current relevant bleaching and temperature data and displays them on the right half of the prpogram window
	download_current_image("https://coralreefwatch.noaa.gov/satellite/bleaching5km/images_current/cur_b05kmnn_max_r07d_baa_45ns.gif", "C:\Users\Joseph Farah\Documents\python\coral\db\current_frame.png")
	im = PIL.Image.open("C:\Users\Joseph Farah\Documents\python\coral\db\current_frame.png")#.convert2byte()
	MAP = ImageTk.PhotoImage(im)
	program_ouput.insert(INSERT, 'MAP CONVERTED TO PNG\n')
	map_display = Label(main, image=MAP)
	map_display.image = MAP # keep a reference!
	map_display.grid(row=2,column=2, columnspan=NUM_BUTTONS_RIGHT_COLUMN)
	program_ouput.insert(INSERT, 'MAP SUCCESSFULLY DISPLAYED\n')

	download_current_image("https://coralreefwatch.noaa.gov/satellite/bleaching5km/images_current/cur_b05kmnn_sst_45ns.gif", "C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_temp.png")
	im_temp = PIL.Image.open("C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_temp.png")#.convert2byte()
	im_temp = im_temp.resize((930, 340), PIL.Image.ANTIALIAS)
	MAP_temp = ImageTk.PhotoImage(im_temp)
	map_display_temp = Label(main, image=MAP_temp)
	map_display_temp.image = MAP_temp # keep a reference!
	map_display_temp.grid(row=4,column=2, columnspan=NUM_BUTTONS_RIGHT_COLUMN)
	program_print('')
	# checks if user supplied an unknown argument and informs them in the PROGRAM_OUTPUT box
	unknown_arg_text = 'UNKNOWN ARGUMENT SUPPLIED BY USER ' + str(unknown_arg)
	program_print(unknown_arg_text)

def ping_noaa():
	'''working on this, apparently you are not allowed to ping the government'''
	os.system("ping ")

def get_date(start, delta):
	'''gets start date'''
	newdate = start + datetime.timedelta(-delta)
	return str(newdate)

def program_print(message):
	global program_ouput
	program_ouput.see(END)
	program_ouput.insert(END, str(message)+'\n')
	program_ouput.see(END)	

def make_img_from_gif(gif_link):
	im = PIL.Image.open(gif_link)
	try:
		i = 0
		program_print("ANALYZING DATA FROM LAST 30 DAYS")
		while 1:		
			im.seek(i)
	  		imframe = im.copy()
	  		if i == 0: 
				palette = imframe.getpalette()
	  		else:
				imframe.putpalette(palette)
	  		yield imframe
	  		i += 1
	except EOFError:
		program_print("EOF ERROR SUCCEESSFULLY AVOIDED, FINISHING GENERATE_FRAMES FUNCTION")

def generate_frames(gif_link, img_save_loc):
	program_print('TRYING TO DELETE /FRAMES/')
	try:
		shutil.rmtree(r"C:\Users\Joseph Farah\Documents\python\coral\db\gif_frames_bleach\frames")
	except WindowsError:
		program_print("FOLDER DOESN'T EXIST, CREATING /FRAMES/")
		pass 
	os.makedirs(r"C:\Users\Joseph Farah\Documents\python\coral\db\gif_frames_bleach\frames")
	for i, frame in enumerate(make_img_from_gif(gif_link)):
		if i >= 0 and i <=10 or i>38:
			continue
		frame.save(r"C:\Users\Joseph Farah\Documents\python\coral\db\gif_frames_bleach\frames\test%d.png" % i,**frame.info)
	program_print('FRAMES CREATED. HISTORICAL DATA READY FOR PIXEL ANALYSIS')

def analyze_historical_images(folder_link):
	program_print("ANALYZING HISTORICAL DATA ONLY")
	for root, dirs, files in os.walk(folder_link):
		for file in files:
			file_path = os.path.normpath(folder_link+'\\'+file)
			program_print(file_path)
			print file_path
			imageObject = PIL.Image.open(file_path) #Can be many different formats.
			tmp_num = file.strip('.png').strip('test')
			get_percentages(imageObject, tmp_num, os.path.normpath(r"C:\Users\Joseph Farah\Documents\python\coral\db\realtime.db"))
	program_print("HISTORICAL ANALYSIS COMPLETE")
	program_print("PIXEL ANALYSIS SUCCESSFUL. GRAPH CAN BE DISPLAYED.")


def ram_save_intro():
	global unknown_arg
	if sys.argv:
		args = list(sys.argv)
		if args[1] == '--v' or args[1] == '-version':
			print 'v0.5.38'
			sys.exit()
		if args[1] == '--g' or args[1] == '-graph':
			generate_graphs(r"C:\Users\Joseph Farah\Documents\python\coral\db\realtime.db")
			sys.exit()
		if args[1] == '--d' or args[1] == '-databases':
			print database_file
			sys.exit()
		unknown_arg = args[1]
	top = Toplevel()
	top.title('Welcome')
	Message(top, text='LOADING MAPS, PLEASE BE PATIENT', padx=20, pady=20).pack()
	top.lift(aboveThis=main)
	top.after(500, top.destroy)

def show_daily_change():
	im = PIL.Image.open("C:\Users\Joseph Farah\Documents\python\coral\db\current_frame.png")#.convert2byte()
	MAP = ImageTk.PhotoImage(im)
	program_ouput.insert(INSERT, 'REALTIME MAP CONVERTED TO PNG\n')
	map_display = Label(main, image=MAP)
	map_display.image = MAP # keep a reference!
	map_display.grid(row=2,column=2, columnspan=3)
	program_ouput.insert(INSERT, 'REALTIME CHANGE MAP SUCCESSFULLY DISPLAYED\n')

def show_cumulative():
	download_current_image("https://coralreefwatch.noaa.gov/satellite/bleaching5km/images_current_composite/cur_b05kmnn_baa_max_45ns.gif", "C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_cumulative.png")
	im = PIL.Image.open("C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_cumulative.png")#.convert2byte()
	MAP = ImageTk.PhotoImage(im)
	program_ouput.insert(INSERT, 'CUMULATIVE MAP CONVERTED TO PNG\n')
	map_display = Label(main, image=MAP)
	map_display.image = MAP # keep a reference!
	map_display.grid(row=2,column=2, columnspan=3)
	program_ouput.insert(INSERT, 'CUMULATIVE MAP SUCCESSFULLY DISPLAYED\n')

def show_forecast():
	download_current_image('https://coralreefwatch.noaa.gov/satellite/bleachingoutlook_cfs/current_images/cur_cfsv2_prob-4mon_v4_alertlevel1_45ns.gif', "C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_forecast.png")
	im = PIL.Image.open("C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_forecast.png")#.convert2byte()
	MAP = ImageTk.PhotoImage(im)
	program_ouput.insert(INSERT, 'CUMULATIVE MAP CONVERTED TO PNG\n')
	map_display = Label(main, image=MAP)
	map_display.image = MAP # keep a reference!
	map_display.grid(row=2,column=2, columnspan=3)
	program_ouput.insert(INSERT, 'FORECAST MAP SUCCESSFULLY DISPLAYED\n')

def depict_ph_increase(x,y,color, imobject):
	program_print(color)
	draw = PIL.ImageDraw.Draw(imobject)
	draw.text((x, y),"<--"+str(ph_change(color,x,y))+' [H+]',(255,255,255))
	imobject.save('tmp-out.gif')
	im_temp = PIL.Image.open("tmp-out.gif")#.convert2byte()
	im_temp = im_temp.resize((930, 340))
	MAP_temp = ImageTk.PhotoImage(im_temp)
	map_display_temp = Label(main, image=MAP_temp)
	map_display_temp.image = MAP_temp # keep a reference!
	map_display_temp.grid(row=4,column=2, columnspan=3)

def read_temp_pixels(temperature_file, rngup, rngdown):
	temp_image_object = PIL.Image.open(temperature_file).convert('RGB')
	#tempdrawimage(temp_image_object)
	(length, width) = get_image_size(temp_image_object)
	(rngxleft, rngxright) = rngup
	(rngyup,rngydown) = rngdown
	print 'the length and width is'
	print length, width
	hotspots = 30;
	for hotspot in range(0,hotspots):
		color = "#ffffff"
		while color == "#ffffff" or color == "#000000" or color == "#505050" or color == "#969696":
			yc = random.randint(rngxleft, rngxright)
			xc = random.randint(rngyup,rngydown)
			color = convert_RGB_HEX(get_pixel_color(PIL.Image.open(temperature_file), xc, yc))
		depict_ph_increase(xc,yc,color, temp_image_object)

def tempdrawimage(imobject):
	im_temp = imobject
	im_temp = im_temp.resize((930, 340), PIL.Image.ANTIALIAS)
	MAP_temp = ImageTk.PhotoImage(im_temp)
	map_display_temp = Label(main, image=MAP_temp)
	map_display_temp.image = MAP_temp # keep a reference!
	map_display_temp.grid(row=4,column=2, columnspan=3)

def ph_change(c, ex, why):
	tempnumdist = [-2,0,5,10,15,20,25,30,35]
	tempdist = [negativetwo,zero,five,ten,fifteen,twenty,twentyfive,thirty,thirtyfive]
	for temperature in tempdist:
		activetemp = temperature
		if c <= activetemp and c > tempdist[tempdist.index(temperature)-1]:
			break
	program_print(activetemp)
	ph_value = round(7.95+0.0114*tempnumdist[tempdist.index(activetemp)]+random.uniform(0,0.5), 3)
	date_value = datetime.datetime.now()
	with open(r"C:\Users\Joseph Farah\Documents\python\coral\db\ph.db", 'a') as ph_db:
		ph_input_str = str(ex) + ',' + str(why) +',' + str(ph_value) + ',' + str(date_value) + '\n'
		ph_db.write(ph_input_str)
	return ph_value


def continuousscan():
	global keepgoing
	keepgoing = 1
	while keepgoing != 0:
		read_temp_pixels(r"C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_temp.png",(40,240),(100,810))
		main.update()


def stopscan():
	global keepgoing
	keepgoing = 0

def ph_vs_bleaching():
	iterations = 5
	keepgoing = -1*iterations
	while keepgoing<0:
		if keepgoing != 0:
			read_temp_pixels(r"C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_temp.png",(40,240),(100,810))
		keepgoing += 1

	ns, w, wa, a1, a2, points = 0,0,0,0,0,0
	labels = ['NO STRESS', 'WATCH', 'WARNING', 'ALERT1', 'ALERT2']
	neutral, increase = 0,0
	with open(r"C:\Users\Joseph Farah\Documents\python\coral\db\ph.db", 'r') as ph_db:
		ph_data = ph_db.read().splitlines()

	data_list = []
	for element in ph_data:
		data_list.append(element.split(','))

	file_path = os.path.normpath("C:\Users\Joseph Farah\Documents\python\coral\db\current_frame.png")
	imageObject = PIL.Image.open(file_path)
	for entry in data_list:
		x = int(entry[0])
		y = int(entry[1])
		pH = float(entry[2])
		color = get_pixel_color(imageObject, x, y)
		color = convert_RGB_HEX(color)
		if pH >= 8.5:
			points += 1
			# checks color of pixel against predefined ranges
			if color == no_stress_color_range:
				ns += 1
				neutral += 1
				continue
			elif color == watch_color_range:
				w += 1
				increase += 1
				continue
			elif color ==  warning_color_range:
				wa += 1
				increase += 1
				continue
			elif color == alert_1_color_range:
				a1 += 1
				increase += 1
				continue
			elif color == alert_2_color_range:
				a2 += 1
				increase += 1
				continue
			else:
				program_print("Error in pH analysis: color not found. Aborting.")
				program_print(color)
				return
	print ns, w, wa, a1, a2
	sizes = [float(ns)/float(points), float(w)/float(points), float(wa)/float(points), float(a1)/float(points), float(a2)/float(points)]
	explode = (0,0.2,0.4,0.6,0.8)
	fig1, ax1 = plt.subplots()
	ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
	        shadow=True, startangle=90)
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	ax1.set_title('Percentages of pH increases that resulted in alert status', 
             bbox={'facecolor':'0.8', 'pad':3})

	plt.show()



def display_hurricane(url):
	top = Toplevel()
	top.title("Displaying weather from around the world")
	
	download_current_image(url, r"C:\Users\Joseph Farah\Documents\python\coral\db\hurricane.png")

	# mappic = Label(top, image=os.path.normpath("C:/Users/Joseph Farah/Documents/python/coral/db/hurricane.png")).pack()

	im_temp = PIL.Image.open("C:/Users/Joseph Farah/Documents/python/coral/db/hurricane.png")#.convert2byte()
	# im_temp = im_temp.resize((930, 340))
	MAP_temp = ImageTk.PhotoImage(im_temp)
	map_display_temp = Label(top, image=MAP_temp)
	map_display_temp.image = MAP_temp # keep a reference!

	map_display_temp.pack()

	button = Button(top, text="Dismiss", command=top.destroy)
	button.pack()
	top.mainloop()

# THE FUNCTIONS STOPS HERE. HERE BE DRAGONS









# smain function running		
# analyze_images()
# generate_graphs("C:\Users\jrfar\Documents\python\coral\db\hist.db")

# buttons and menus and crap
bleaching_database_view = Text(main, bg = "black", fg = "white", insertbackground = "white",tabs = ("1c"))
bleaching_database_view.grid(row = 2, column = 0, columnspan=2)
program_ouput = Text(main, bg = "black", fg = "white", insertbackground = "white",tabs = ("1c"), height=18)
program_ouput.grid(row = 4, column = 0, columnspan=2)
menubar = Menu(main)
menubar.add_command(label="Quit!", command=main.quit)
menubar.add_command(label="Get data from the last 30 days!", command=lambda:generate_frames(r"C:\Users\Joseph Farah\Documents\python\coral\db\gif_frames_bleach\baa-max_animation_30day_45ns.gif", "C:\Users\Joseph Farah\Documents\python\coral\db\gif_frames_bleach\frames"))
menubar.add_command(label="Analyze historical data!", command=lambda:analyze_historical_images(os.path.normpath(r"C:\Users\Joseph Farah\Documents\python\coral\db\gif_frames_bleach\frames\\")))
menubar.add_command(label="Select database file!", command=get_database)
menubar.add_command(label="Save the current graph!", command=lambda:generate_graphs(r"C:\Users\Joseph Farah\Documents\python\coral\db\realtime.db"))
menubar.add_command(label="Map pH change!", command=lambda:read_temp_pixels(r"C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_temp.png",(40,240),(100,810)))

ph = Menu(menubar, tearoff=0)
ph.add_command(label="Atlantic Ocean Top", command=lambda:read_temp_pixels(r"C:\Users\Joseph Farah\Documents\python\coral\db\current_frame_temp.png",(68,132),(710,810) ))
ph.add_command(label="Continuous Scan", command=continuousscan)
ph.add_command(label="Stop Scan", command=stopscan)
ph.add_command(label="Collect pH data", command=ph_vs_bleaching)
ph.add_separator()
ph.add_command(label="Exit", command=main.quit)
menubar.add_cascade(label="pH Mapping", menu=ph)

weather = Menu(menubar, tearoff=0)
weather.add_command(label='View Pacific Hurricane alerts', command=lambda:display_hurricane("http://www.nhc.noaa.gov/xgtwo/two_pac_5d0.png"))
weather.add_command(label='View Atlantic Hurricane alerts', command=lambda:display_hurricane("http://www.nhc.noaa.gov/xgtwo/two_atl_5d0.png"))
weather.add_command(label='View Global Temperature Hotspots', command=lambda:display_hurricane("http://www.ospo.noaa.gov/data/cb/hotspots/hotspotgcurrent.gif"))
menubar.add_cascade(label="Worldwide Weather Watch", menu=weather)


Label(main,text = 'REALTIME DATABASE FILE VIEW').grid(row=1, column=0,columnspan=2)
Label(main,text = 'PROGRAM OUTPUT').grid(row=3, column=0,columnspan=2)
Button(main,text='Get percentages!', command=lambda:analyze_cumulative()).grid(row = 0, column=1)
Button(main,text='Show graph', command=lambda:generate_graphs(r"C:\Users\Joseph Farah\Documents\python\coral\db\realtime.db")).grid(row = 0, column=0)
Button(main, text = 'Show daily change map/Refresh daily change map', command=show_daily_change).grid(row = 1,column = 2)
Button(main, text = 'Show cumulative reef stress (all datasets)', command=show_cumulative).grid(row = 1,column = 3)
Button(main, text = 'Show reef stress forecast', command=show_forecast).grid(row = 1,column = 4)
main.config(menu=menubar)
main.after(0,ram_save_intro)
main.after(500, startup_function)
main.iconbitmap(default='../coralicon.ico')
main.state('zoomed')
main.wm_title("CORAL: Real-time reef bleaching tracker")
main.mainloop()
