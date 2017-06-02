# written by Joseph Farah on April 21, 2017

# consider adding try/except for pillow
import PIL.Image
import os
import datetime
import time
import matplotlib.pyplot as plt
from Tkinter import *
from tkFileDialog import askopenfilename as selectFILE
import tkMessageBox as tkmb
# not necessary for the historical program because only this one downloads crap from the internet
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
		for w in range(120,121):
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
	return pixels

def get_percentages(im):
	global no_stress_color_range, watch_color_range, warning_color_range, alert_1_color_range, alert_2_color_range, no_stress, watch_color, warning_color, alert_1_color, alert_2_color, black_color_range, black, land_range, land
	no_stress, watch_color, warning_color, alert_1_color, alert_2_color = 0,0,0,0,0
	pixels  = float(count_pixels(im))
	print pixels, no_stress, watch_color, warning_color, alert_1_color, alert_2_color
	# the values in the database will go in order of the alert levels, with a timestamp at the beginning delimited by a |
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	database_input_list = [st, no_stress/pixels, watch_color/pixels, warning_color/pixels, alert_1_color/pixels, alert_2_color/pixels]
	for element in database_input_list:
		if database_input_list.index(element) == 0:
			continue
		database_input_list[database_input_list.index(element)] == element
	database_input = "".join(str(database_input_list))
	print database_input
	with open(os.path.normpath(r"C:\Users\jrfar\Documents\python\coral\db\realtime.db"), "a") as database:
		database.write(database_input+'\n')	

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
			x_values.append(t)

	fig, ax = plt.subplots()
	#plt.ion()
	# ax.plot(x_values,no_stress_points, color="black", label = 'NO STRESS')
	print len(x_values), len(watch_data_points), len(warning_data_points), len(alert_1_data_points), len(alert_2_data_points)
	ax.plot(x_values, watch_data_points, color="blue", label = 'WATCH')
	ax.plot(x_values, warning_data_points, color="yellow", label = 'WARNING')
	ax.plot(x_values, alert_1_data_points, color="orange", label = 'ALERT 1')
	ax.plot(x_values, alert_2_data_points, color="red", label = 'ALERT 2')
	legend = ax.legend(loc='upper right', shadow=True)
	for label in legend.get_texts():
		label.set_fontsize('small')

	plt.show()

def analyze_images():
	download_current_image()
	file_path = os.path.normpath("C:\Users\jrfar\Documents\python\coral\db\current_frame.png")
	imageObject = PIL.Image.open(file_path) #Can be many different formats.
	get_percentages(imageObject)
	tkmb.showinfo("Process Completed","Process complete, GRAPH ready to be GENERATED")	

def download_current_image():
	urllib.urlretrieve("https://coralreefwatch.noaa.gov/satellite/bleaching5km/images_current/cur_webhome_b05kmnn_max_r07d_baa_45ns.gif", "C:\Users\jrfar\Documents\python\coral\db\current_frame.png")
	print 'Image retrieved'

def get_database():
	print 'test'

def save_graph():
	print 'test'


# smain function running		
# analyze_images()
# generate_graphs("C:\Users\jrfar\Documents\python\coral\db\hist.db")

# buttons and menus and crap
menubar = Menu(main)
menubar.add_command(label="Quit!", command=main.quit)
menubar.add_command(label="Select database file!", command=get_database)
menubar.add_command(label="Save the current graph!", command=lambda:generate_graphs("C:\Users\jrfar\Documents\python\coral\db\realtime.db"))

Button(main,text='Get percentages!', command=lambda:analyze_images()).grid(row = 0, column=1)
Button(main,text='Show graph', command=lambda:generate_graphs(r"C:\Users\jrfar\Documents\python\coral\db\realtime.db")).grid(row = 0, column=2)

main.config(menu=menubar)
main.mainloop()
