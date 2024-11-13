from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import platform
from kivy.core.window import Window
from kivy.clock import Clock,mainthread

if platform=='android':
	#from android.storage import app_storage_path
	from w4k.webview4kivy import GLWebView

class MyLayout(FloatLayout):

	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		Window.bind(on_keyboard=self.Android_back_click)
		

	def _start(self,):
		self.ids.gw.connect_webview()
	def _stop(self):
		self.ids.gw.disconnect_webview()

		

	def Android_back_click(self,window,key,*largs):
		if key == 27:
			print('back')
			self.ids.gw.go_back()
			return True



class MyApp(App):
	def build(self):
		if platform=='android':pass
			#from android_webview import immersive_mode
			#immersive_mode(status='enable')
		return MyLayout()
	
	
if __name__=="__main__":
	MyApp().run()