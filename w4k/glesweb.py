from jnius import autoclass, PythonJavaClass, java_method
from kivy.clock import Clock,mainthread
from kivy.graphics.texture import Texture
from kivy.graphics import Fbo, Callback, Rectangle
from .android_webview import WebView as JWebView
#import threading

SurfaceTexture = autoclass('android.graphics.SurfaceTexture')
Surface=autoclass('android.view.Surface')
GL_TEXTURE_EXTERNAL_OES = autoclass('android.opengl.GLES11Ext').GL_TEXTURE_EXTERNAL_OES
#ImageFormat = autoclass('android.graphics.ImageFormat')



# class PreviewCallback(PythonJavaClass):
#     """
#     Interface used to get back the preview frame of the Android Camera
#     """
#     __javainterfaces__ = ('android.hardware.Camera$PreviewCallback', )

#     def __init__(self, callback):
#         super(PreviewCallback, self).__init__()
#         self._callback = callback

#     @java_method('([BLandroid/hardware/Camera;)V')
#     def onPreviewFrame(self, data, camera):
#         self._callback(data, camera)

 
class GLESWebView:
    """
    Implementation of WebviewBase using Android API
    """
    _update_ev = None
    _texture=None
    _android_webview=None

    def __init__(self,url,enable_javascript = True,enable_downloads = False,\
            enable_zoom = True,width=800,height=700,fps=30,callback=None,**kwargs):
        super(GLESWebView,self).__init__(**kwargs)
        self.callback=callback
        self.url=url
        self._width=width
        self._height=height
        self._fps=fps
        self._enable_javascript=enable_javascript
        self._enable_downloads=enable_downloads
        self._enable_zoom=enable_zoom

        self._android_webview=JWebView(self.url, enable_javascript = self._enable_javascript,enable_downloads = self._enable_downloads,\
            enable_zoom = self._enable_zoom,width=self._width,height=self._height,callback=self.callback,**kwargs)
        self._android_webview._init()

        self._resolution=(self._width,self._height)
        self._size=(self._width,self._height)
       
        self._web_texture = Texture(width=self._width, height=self._height,
                                       target=GL_TEXTURE_EXTERNAL_OES,
                                       colorfmt='rgba')
        self._surface_texture = SurfaceTexture(int(self._web_texture.id))

        self._surface_texture.setDefaultBufferSize(self._width,self._height)
        self._surface=Surface(self._surface_texture)
        self._android_webview.draw(self._surface)
    

        
        self._fbo = Fbo(size=self._size)
        self._fbo['resolution'] = (float(self._width), float(self._height))
        self._fbo.shader.fs = '''
            #extension GL_OES_EGL_image_external : require
            #ifdef GL_ES
                precision highp float;
            #endif

            /* Outputs from the vertex shader */
            varying vec4 frag_color;
            varying vec2 tex_coord0;

            /* uniform texture samplers */
            uniform sampler2D texture0;
            uniform samplerExternalOES texture1;
            uniform vec2 resolution;

            void main()
            {
                vec2 coord = vec2(tex_coord0.y * (
                    resolution.y / resolution.x), 1. -tex_coord0.x);
                gl_FragColor = texture2D(texture1, tex_coord0);
            }
        '''
        with self._fbo:
            self._texture_cb = Callback(lambda instr:
                                        self._web_texture.bind)
            Rectangle(size=self._resolution)

        #print('from glesweb file ')
    
    def __del__(self):
        self._destroy()


    def _start_update(self):
        self._start()


    def _stop_update(self):
        self._stop()

    

    def _destroy(self):
        if self._android_webview is None:
            return
        self._stop()

        # clear texture and it'll be reset in `_update` pointing to new FBO
        self._texture = None
        del self._fbo, self._surface_texture, self._web_texture,self._surface



    def _load_url(self,url):
        if self._android_webview:
            self._android_webview.load_url(url)

    def _back_pressed(self):
        self._android_webview._back_pressed()
    def _resize(self,size):
        self._android_webview._size(size)
    

   
#########################################################

#########################################################
    
    def _refresh_fbo(self):
        self._texture_cb.ask_update()
        self._fbo.draw()
    
    #It will start update texture data from Android webview to Kivy 
    def _start(self):
        if self._update_ev is not None:
           self._update_ev.cancel()
        self._update_ev = Clock.schedule_interval(self._update, 1 / self._fps)


    #This will stop update 
    def _stop(self):
        if self._update_ev is not None:
            self._update_ev.cancel()
        self._update_ev = None
        

# This Function will update texture data from android to kivy by default fps=30
    def _update(self, dt):
        self._surface_texture.updateTexImage()
        self._android_webview.draw(self._surface)
        self._refresh_fbo()
        if self._texture is None:
            self._texture = self._fbo.texture
        self._callback(self._texture)
            
    
    #@mainthread
    def _callback(self,texture):
        self.callback(texture)
        #print('callback ====',texture)

    def touch_down(self,x,y,wid):
        self._android_webview.touch_down(x, y,wid)
    def touch_move(self,x,y,wid):
        self._android_webview.touch_move(x, y,wid)
    def touch_up(self,x,y,wid):
        self._android_webview.touch_up(x, y,wid)



     
