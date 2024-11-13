# Android Webview Implementation using GL Texture Rendering 
# Programmer SK SAHIL (Sahil-pixel)

from kivy.uix.image import Image
from kivy.clock import Clock,mainthread
from kivy.properties import ObjectProperty,StringProperty,BooleanProperty,NumericProperty
from .glesweb import GLESWebView

class GLWebView(Image):
	_texture=ObjectProperty(None)
	_glweb=None
	url=StringProperty('https://www.google.com/')
	enable_javascript=BooleanProperty(True)
	update_fps=NumericProperty(30)
	_state=True

	def __init__(self,**kwargs):
		super(GLWebView,self).__init__(**kwargs)
		Clock.schedule_once(self._next_frame,)
	
	def _next_frame(self,dt):
		#url='https://www.google.com/'
		self._glweb=GLESWebView(self.url,callback=self._callback,\
			height=self.height,width=self.width,\
			enable_javascript = self.enable_javascript,fps=self.update_fps)
		self.connect_webview()
		self._state=True
		
    # Load Url 
	def load_url(self,url):
		self._glweb._load_url(url)

	#To Start update texture at 1/fps seconds
	def connect_webview(self):
		self._glweb._start_update()
		self._state=True
	
	#To Stop update texture at 1/fps seconds 
	def disconnect_webview(self):
		self._glweb._stop_update()
		self.texture=None
		self._state=False
	
	#This will destroy objects also 
	def destroy_webview(self):
		self._glweb._destroy()
		self._state=False

	#This call back update texture data on Image Widget 
	def _callback(self,_texture):
		if not self.texture:
			#print('call _ back ') 
			self.texture=_texture
		self.canvas.ask_update()

	def on_size(self,obj,size):
		if self._glweb:
			self._glweb._resize(size)
		#print('size===',size)

	def on_pos(self,obj,pos):pass

		#print('pos',pos)


	

	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			if self._glweb and self._state:
				self._glweb.touch_down(touch.x,touch.y,self)
				#print('touch down send from kivy side ')
		return super().on_touch_down(touch)
	
	def on_touch_move(self, touch):
		if self.collide_point(*touch.pos):
		#print('cliide')
			if self._glweb and self._state:
				self._glweb.touch_move(touch.x,touch.y,self)
				#print('touch move send from kivy side ')

		return super().on_touch_move(touch)

	def on_touch_up(self, touch):
		#print("touch up in kivy ")
		if self.collide_point(*touch.pos):
			if self._glweb and self._state:
				self._glweb.touch_up(touch.x,touch.y,self)
				#print('touch up send from kivy side ')
		return super().on_touch_move(touch)
	
	def go_back(self):
		#print('go back ')
		if self._glweb:
			self._glweb._back_pressed()


