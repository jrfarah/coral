import PIL.Image
import os

def make_img_from_gif(gif_link):
	im = PIL.Image.open(gif_link)
	i = 0
	print("ANALYZING DATA FROM LAST 30 DAYS")
	while 1:		
		im.seek(i)
		print i
  		imframe = im.copy()
  		if i == 0: 
			palette = imframe.getpalette()
  		else:
			imframe.putpalette(palette)
  		yield imframe
  		i += 1



#make_img_from_gif(os.path.normpath("C:\Users\jrfar\Documents\python\coral\db\gif_frames_bleach\baa-max_animation_30day_45ns.gif"))
for i, frame in enumerate(make_img_from_gif(r"C:\Users\jrfar\Documents\python\coral\db\gif_frames_bleach\baa-max_animation_30day_45ns.gif")):
	if i => 0 and i <=10:
		continue
	frame.save(r'C:\Users\jrfar\Documents\python\coral\db\gif_frames_bleach\frames\test%d.png' % i,**frame.info)