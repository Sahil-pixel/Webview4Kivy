# Android Webview Implementation using OpenGL texture rendering for Kivy 
#### Description
This Webview for Android. Which is Kivy Widget not an Overlay. This can be use to render web pages or Katex (Latex Things).

#### Problems  
- This Webview is still now limited. We can not watch DRM Protected Contents.
- Android Keyboard is not showing .

#### Performance on the physical device [Youtube Video](https://youtu.be/etc5M0DvX-A?si=STmBrpc8NQXKCpEo).

#### Example Code
```
#main.py 
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


#myapp.kv
<MyLayout>:
	canvas.before:
		Color:
			rgba:[1,1,1,1]
		Rectangle:
			pos:self.pos
			size:self.size
	TextInput:
		id:ti

		pos_hint: {'center_x': 0.5,'y':0.92}
		size_hint:0.8,None
		height:dp(50)
		hint_text:'Enter Url'


	GLWebView:
		url:'https://google.com/'
		enable_javascript:True
		update_fps:30
		size_hint: (None, None)
		size:900,1600
		pos:100,400
		id:gw
		


		
	Button:
		pos_hint: {'center_x': 0.2,'y':0.05}
		size_hint: (None, None)
		size:dp(100),dp(50)
		text: 'start update'
		on_release:root._start()
	Button:
		pos_hint: {'center_x': 0.5,'y':0.05}
		size_hint: (None,None)
		size:dp(100),dp(50)
		text:'load url'
		on_release:gw.load_url(ti.text)
	
	Button:
		pos_hint: {'x': 0.7,'y':0.05}
		size_hint: (None, None)
		size:dp(100),dp(50)
		text: 'stop update'
		on_release:root._stop()
	

	

``` 