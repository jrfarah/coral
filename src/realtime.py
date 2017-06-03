# written by Joseph Farah on April 21, 2017
# Last updated June 2nd 2017

# consider adding try/except for pillow
import PIL.Image
from PIL import ImageTk
import os
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

# count vars, global 
no_stress_color_range = '#ffffff'
watch_color_range = '#c8ff32'
warning_color_range = "#faaa0a"
alert_1_color_range = "#f00000"
alert_2_color_range = "#960000"
black_color_range = "#000000"
land_range = "#c8c8c8"

no_stress = 0.0
watch_color = 0.0
warning_color = 0.0
alert_1_color = 0.0
alert_2_color = 0.0
black = 0.0
land = 0.0

dataset = []
x_values = []
no_stress_points = []
watch_data_points = []
warning_data_points = []
alert_1_data_points = []
alert_2_data_points = []

database_file = r"C:\Users\jrfar\Documents\python\coral\db\realtime.db"

main = Tk()

def get_pixel_color(image_object, x,y):
	# gets the color at a specificed pixel
	rgb_im = image_object.convert('RGB')
	r, g, b = rgb_im.getpixel((x, y))

	return r,g,b

def get_image_size(image_object):
	return image_object.size

def clamp(random_var_name_1):
  	return max(0, min(random_var_name_1, 255))

def convert_RGB_HEX(color_tuple):
	return "#{0:02x}{1:02x}{2:02x}".format(clamp(color_tuple[0]), clamp(color_tuple[1]), clamp(color_tuple[2]))

def count_pixels(im):
	global no_stress_color_range, watch_color_range, warning_color_range, alert_1_color_range, alert_2_color_range, no_stress, watch_color, warning_color, alert_1_color, alert_2_color, black_color_range, black, land_range, land
	(length, width) = get_image_size(im)
	print length, width
	pixels = 0
	color = get_pixel_color(im, 225, 95)
	print convert_RGB_HEX(color)
	for l in range(length): 
		for w in range(120,121): # this range is ONLY for testing purposes, will be replaced with "width"
			pixels += 1
			color = get_pixel_color(im, l, w)
			color = convert_RGB_HEX(color)
			if color == no_stress_color_range:
				no_stress += 1
			elif color == watch_color_range:
				watch_color += 1
				continue
			elif color ==  warning_color_range:
				warning_color += 1
			elif color == alert_1_color_range:
				alert_1_color += 1
			elif color == alert_2_color_range:
				alert_2_color += 1
			elif color == black_color_range:
				black += 1
			elif color == land_range:
				land += 1
	program_print("PIXEL ANALYSIS SUCCESSFUL. GRAPH CAN BE DISPLAYED.")
	return pixels

def get_percentages(im):
	global no_stress_color_range, watch_color_range, warning_color_range, alert_1_color_range, alert_2_color_range, no_stress, watch_color, warning_color, alert_1_color, alert_2_color, black_color_range, black, land_range, land, database_file, bleaching_database_view
	no_stress, watch_color, warning_color, alert_1_color, alert_2_color = 0,0,0,0,0
	pixels  = float(count_pixels(im))
	print pixels, no_stress, watch_color, warning_color, alert_1_color, alert_2_color
	# the values in the database will go in order of the alert levels, with a timestamp at the beginning delimited by a |
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	program_print("GETTING PERCENTAGES")
	program_print("GETTING DATE TIME")
	program_print(ts)
	database_input_list = [st, no_stress/pixels, watch_color/pixels, warning_color/pixels, alert_1_color/pixels, alert_2_color/pixels]
	for element in database_input_list:
		if database_input_list.index(element) == 0:
			continue
		database_input_list[database_input_list.index(element)] == element
	database_input = "".join(str(database_input_list))
	print database_input
	with open(os.path.normpath(database_file), "a") as database:
		database.write(database_input+'\n')	
	with open(database_file, "r") as database:
		bleaching_database_view.delete('1.0', END)
		info_tmp = database.read()
		bleaching_database_view.insert(INSERT, info_tmp)

def generate_graphs(database_file):
	global dataset, x_values, no_stress, watch_data_points, warning_data_points, alert_1_data_points, alert_2_data_points
	data = []
	dataset = []
	no_stress_points = []
	watch_data_points = []
	warning_data_points = []
	alert_1_data_points = []
	alert_2_data_points = []
	x_values = []
	x_values_num = []
	with open(database_file, "r") as database:
		data = database.read().splitlines()
		for d1 in data:
			tmp = d1.strip('[]')
			dataset.append([d.strip() for d in tmp.split(',')])
		for element in dataset:
			no_stress_points.append(float(element[1]))
			watch_data_points.append(float(element[2]))
			warning_data_points.append(float(element[3]))
			alert_1_data_points.append(float(element[4]))
			alert_2_data_points.append(float(element[5]))
		for t in range(len(no_stress_points)):
			x_values.append(str(dataset[t][0]))
			x_values_num.append(t)

	print x_values_num, x_values
	fig, ax = plt.subplots(1,1)
	ax.set_axis_bgcolor((0, 0, 0))
	#plt.ion()
	# ax.plot(x_values,no_stress_points, color="black", label = 'NO STRESS')
	print len(x_values), len(watch_data_points), len(warning_data_points), len(alert_1_data_points), len(alert_2_data_points)
	#ax.set_xticks(x_values_num)
	#ax.set_xticklabels(x_values_num, x_values)
	ax.plot(x_values_num, watch_data_points, color="blue", label = 'WATCH')
	ax.plot(x_values_num, warning_data_points, color="yellow", label = 'WARNING')
	ax.plot(x_values_num, alert_1_data_points, color="orange", label = 'ALERT 1')
	ax.plot(x_values_num, alert_2_data_points, color="red", label = 'ALERT 2')
	plt.xlabel('Days since the first measurement in the dataset {0}'.format(str(dataset[t][0])))
	plt.ylabel('Percentage of reef at various alert levels')
	legend = ax.legend(loc='upper right', shadow=True)
	for label in legend.get_texts():
		label.set_fontsize('small')

	plt.show()

def analyze_images():
	download_current_image("https://coralreefwatch.noaa.gov/satellite/bleaching5km/images_current/cur_b05kmnn_max_r07d_baa_45ns.gif", "C:\Users\jrfar\Documents\python\coral\db\current_frame.png")
	download_current_image("https://coralreefwatch.noaa.gov/satellite/bleaching5km/index_5km_dhw.php", "C:\Users\jrfar\Documents\python\coral\db\current_frame_temp.png")
	file_path = os.path.normpath("C:\Users\jrfar\Documents\python\coral\db\current_frame.png")
	imageObject = PIL.Image.open(file_path) #Can be many different formats.

	get_percentages(imageObject)
	tkmb.showinfo("Process Completed","Process complete, GRAPH ready to be GENERATED")	

def download_current_image(url_link, path_to_save):
	urllib.urlretrieve(url_link, path_to_save)
	print 'Image retrieved'

def get_database():
	global database_file
	databse_file = selectFILE()
	tkmb.showinfo("File Selected","DATABASE FILE SELECTED")	

def save_graph():
	print 'test'

def startup_function():
	with open(database_file, "r") as database:
		bleaching_database_view.delete('1.0', END)
		info_tmp = database.read()
		bleaching_database_view.insert(INSERT, info_tmp)	
	with open("startuptext.txt", "r") as info:
		program_ouput.delete('1.0', END)
		info_tmp = info.read()
		program_ouput.insert(INSERT, info_tmp)	
	
	im = PIL.Image.open("C:\Users\jrfar\Documents\python\coral\db\current_frame.png")#.convert2byte()
	MAP = ImageTk.PhotoImage(im)
	program_ouput.insert(INSERT, 'MAP CONVERTED TO PNG\n')
	map_display = Label(main, image=MAP)
	map_display.image = MAP # keep a reference!
	map_display.grid(row=2,column=3, columnspan=2)
	program_ouput.insert(INSERT, 'MAP SUCCESSFULLY DISPLAYED\n')

	download_current_image("https://coralreefwatch.noaa.gov/satellite/bleaching5km/images_current/cur_b05kmnn_sst_45ns.gif", "C:\Users\jrfar\Documents\python\coral\db\current_frame_temp.png")
	im_temp = PIL.Image.open("C:\Users\jrfar\Documents\python\coral\db\current_frame_temp.png")#.convert2byte()
	im_temp = im_temp.resize((930, 340), PIL.Image.ANTIALIAS)
	MAP_temp = ImageTk.PhotoImage(im_temp)
	map_display_temp = Label(main, image=MAP_temp)
	map_display_temp.image = MAP_temp # keep a reference!
	map_display_temp.grid(row=4,column=3, columnspan=2)

def ping_noaa():
	os.system("ping ")

def program_print(message):
	global program_ouput
	program_ouput.insert(INSERT, str(message)+'\n')
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
		shutil.rmtree(r"C:\Users\jrfar\Documents\python\coral\db\gif_frames_bleach\frames")
	except WindowsError:
		program_print("FOLDER DOESN'T EXIST, CREATING /FRAMES/")
		pass 
	os.makedirs(r"C:\Users\jrfar\Documents\python\coral\db\gif_frames_bleach\frames")
	for i, frame in enumerate(make_img_from_gif(gif_link)):
		if i >= 0 and i <=10:
			continue
		frame.save(r'C:\Users\jrfar\Documents\python\coral\db\gif_frames_bleach\frames\test%d.png' % i,**frame.info)
	program_print('HISTORICAL FRAMES CREATED, LAST 30 DAYS PREPARED FOR PIXEL ANALYSIS')	

def analyze_historical_images(folder_link):
	program_print("ANALYZING HISTORICAL DATA ONLY")
	for root, dirs, files in os.walk(folder_link):
		for file in files:
			file_path = os.path.normpath(folder_link+'\\'+file)
			program_print(file_path)
			print file_path
			imageObject = PIL.Image.open(file_path) #Can be many different formats.
			get_percentages(imageObject)
	program_print("HISTORICAL ANALYSIS COMPLETE")


def ram_save_intro():
    top = Toplevel()
    top.title('Welcome')
    Message(top, text='LOADING MAPS, PLEASE BE PATIENT', padx=20, pady=20).pack()
    top.lift(aboveThis=main)
    top.after(500, top.destroy)

# smain function running		
# analyze_images()
# generate_graphs("C:\Users\jrfar\Documents\python\coral\db\hist.db")

# buttons and menus and crap
bleaching_database_view = Text(main, bg = "black", fg = "white", insertbackground = "white",tabs = ("1c"))
bleaching_database_view.grid(row = 2, column = 0, columnspan=2)
program_ouput = Text(main, bg = "black", fg = "white", insertbackground = "white",tabs = ("1c"))
program_ouput.grid(row = 4, column = 0, columnspan=2)
menubar = Menu(main)
menubar.add_command(label="Quit!", command=main.quit)
menubar.add_command(label="Get data from the last 30 days!", command=lambda:generate_frames(r"C:\Users\jrfar\Documents\python\coral\db\gif_frames_bleach\baa-max_animation_30day_45ns.gif", "C:\Users\jrfar\Documents\python\coral\db\gif_frames_bleach\frames"))
menubar.add_command(label="Analyze historical data!", command=lambda:analyze_historical_images(os.path.normpath(r"C:\Users\jrfar\Documents\python\coral\db\gif_frames_bleach\frames\\")))
menubar.add_command(label="Select database file!", command=get_database)
menubar.add_command(label="Save the current graph!", command=lambda:generate_graphs(r"C:\Users\jrfar\Documents\python\coral\db\realtime.db"))
Label(main,text = 'REALTIME DATABASE FILE VIEW').grid(row=1, column=0,columnspan=2)
Label(main,text = 'PROGRAM OUTPUT').grid(row=3, column=0,columnspan=2)
Button(main,text='Get percentages!', command=lambda:analyze_images()).grid(row = 0, column=1)
Button(main,text='Show graph', command=lambda:generate_graphs(r"C:\Users\jrfar\Documents\python\coral\db\realtime.db")).grid(row = 0, column=0)

main.config(menu=menubar)

main.after(0,ram_save_intro)
main.after(500, startup_function)
main.mainloop()
