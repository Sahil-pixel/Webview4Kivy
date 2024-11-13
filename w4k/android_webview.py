# Android **only** HTML viewer, always full screen.
#
# Back button or gesture has the usual browser behavior, except for the final
# back event which returns the UI to the view before the browser was opened.
#
# Base Class:  https://kivy.org/doc/stable/api-kivy.uix.modalview.html 
#
# Requires: android.permissions = INTERNET
# Uses:     orientation = landscape, portrait, or all
# Arguments:
# url               : required string,  https://   file:// (content://  ?) 
# enable_javascript : optional boolean, defaults False 
# enable_downloads  : optional boolean, defaults False 
# enable_zoom       : optional boolean, defaults False 
#
# Downloads are delivered to app storage see downloads_directory() below.
#
# Tested on api=27 and api=30
# 
# Note:
#    For api>27   http://  gives net::ERR_CLEARTEXT_NOT_PERMITTED 
#    This is Android implemented behavior.
#
# Source https://github.com/Android-for-Python/Webview-Example



from functools import partial
from android.runnable import run_on_ui_thread
from jnius import autoclass, cast, PythonJavaClass, java_method

WebViewA = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
WebSettings=autoclass('android.webkit.WebSettings')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
#LinearLayout = autoclass('android.widget.LinearLayout')
FrameLayout=autoclass('android.widget.FrameLayout')
KeyEvent = autoclass('android.view.KeyEvent')
ViewGroup = autoclass('android.view.ViewGroup')
View= autoclass('android.view.View')
MeasureSpec=autoclass('android.view.View$MeasureSpec')
DownloadManager = autoclass('android.app.DownloadManager')
DownloadManagerRequest = autoclass('android.app.DownloadManager$Request')
Uri = autoclass('android.net.Uri')
Environment = autoclass('android.os.Environment')
Context = autoclass('android.content.Context')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Canvas=autoclass("android.graphics.Canvas")
Point=autoclass('android.graphics.Point')
Rect=autoclass('android.graphics.Rect') 
MotionEvent=autoclass('android.view.MotionEvent')
SystemClock=autoclass('android.os.SystemClock')
View=autoclass('android.view.View')
mActivity=PythonActivity.mActivity
###########not using
class DownloadListener(PythonJavaClass):
    #https://stackoverflow.com/questions/10069050/download-file-inside-webview
    __javacontext__ = 'app'
    __javainterfaces__ = ['android/webkit/DownloadListener']

    @java_method('(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;J)V')
    def onDownloadStart(self, url, userAgent, contentDisposition, mimetype,
                        contentLength):
        mActivity = PythonActivity.mActivity 
        context =  mActivity.getApplicationContext()
        visibility = DownloadManagerRequest.VISIBILITY_VISIBLE_NOTIFY_COMPLETED
        dir_type = Environment.DIRECTORY_DOWNLOADS
        uri = Uri.parse(url)
        filepath = uri.getLastPathSegment()
        request = DownloadManagerRequest(uri)
        request.setNotificationVisibility(visibility)
        request.setDestinationInExternalFilesDir(context,dir_type, filepath)
        dm = cast(DownloadManager,
                  mActivity.getSystemService(Context.DOWNLOAD_SERVICE))
        dm.enqueue(request)

###########i am using back button 
class KeyListener(PythonJavaClass):
    __javacontext__ = 'app'
    __javainterfaces__ = ['android/view/View$OnKeyListener']

    def __init__(self, listener):
        super().__init__()
        self.listener = listener

    @java_method('(Landroid/view/View;ILandroid/view/KeyEvent;)Z')
    def onKey(self, v, key_code, event):
        if event.getAction() == KeyEvent.ACTION_DOWN and\
           key_code == KeyEvent.KEYCODE_BACK: 
            return self.listener()

### This listner is not working 
## The idea is to call function in kivy so we can open keyboard in kivy side
class FocusChangeListener(PythonJavaClass):
    __javacontext__ = 'app'
    __javainterfaces__ = ['android/view/View$OnFocusChangeListener']

    def __init__(self, listener):
        super().__init__()
        self.listener = listener

    @java_method('(Landroid/view/View;Z)V')
    def onFocusChange(self, v, hasfocus):
        print('From focus listener ===',hasfocus)
        #if hasfocus:
            #self.listener()


        #return self.listener()
        
###########i am using this 
class WebView:
    # https://developer.android.com/reference/android/webkit/WebView
    texture=None
    def __init__(self, url, enable_javascript = True, enable_downloads = False,
                 enable_zoom = True,width=800,height=700,callback=None,**kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.enable_javascript =  enable_javascript
        self.enable_downloads = enable_downloads
        self.enable_zoom = enable_zoom
        self.webview = None
        self.enable_dismiss = True
        self.width=width
        self.height=height
        self.layout=None
        self.callback=callback
        self.texture=None
        #self._init()

    @run_on_ui_thread     
    def _init(self):
        #mActivity = PythonActivity.mActivity 
        self.webview = WebViewA(mActivity)
        self.webview.setWebViewClient(WebViewClient())
        self.webview.getSettings().setJavaScriptEnabled(self.enable_javascript)
        self.webview.getSettings().setBuiltInZoomControls(self.enable_zoom)
        self.webview.getSettings().setDisplayZoomControls(False)
        self.webview.getSettings().setAllowFileAccess(True) #default False api>29
        self.webview.requestFocus(View.FOCUS_DOWN)
        settings=self.webview.getSettings()
        settings.setMediaPlaybackRequiresUserGesture(False)
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW)

        self.frameLayout=FrameLayout(mActivity.getApplicationContext())
        webParams = LayoutParams(self.width,self.height)
        self.frameLayout.addView(self.webview, webParams)
        widthSpec = MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED)
        heightSpec = MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED)


        #self.layout = LinearLayout(mActivity)
        #self.layout.setOrientation(LinearLayout.VERTICAL)
        #self.layout.addView(self.webview, self.width, self.height)
        


        #mActivity.addContentView(self.layout, LayoutParams(-1,-1))
        self.frameLayout.measure(widthSpec, heightSpec)
        self.frameLayout.layout(0, 0, self.frameLayout.getMeasuredWidth(), self.frameLayout.getMeasuredHeight())
        self.frameLayout.invalidate()
        


        self._focus_change_listner=FocusChangeListener(self._focus_change)
        #print(self._focus_change_listner)

        self.webview.setOnKeyListener(KeyListener(self._back_pressed))
        self.webview.setOnFocusChangeListener(self._focus_change_listner)

        if self.enable_downloads:
            self.webview.setDownloadListener(DownloadListener())
        #self.webview = self.webview
        #self.layout = layout
        #self._size(None,None)
        self.config = mActivity.getResources().getConfiguration()
        self.metric = mActivity.getResources().getDisplayMetrics()
        self.status=True
        self.screen_width,self.screen_height=get_screen_size()
        self.screen_full_height=get_fullScreen_height()
        #print("===",self.screen_full_height,self.screen_height)
        try:
            self.webview.loadUrl(self.url)
        except Exception as e:            
            print('Webview.on_open(): ' + str(e))
            self.dismiss()  
    def _focus_change(self):pass
      
    def _dismiss(self):
        if self.enable_dismiss:
            self.enable_dismiss = False
            #parent = cast(ViewGroup, self.layout.getParent())
            #if parent is not None: parent.removeView(self.layout)
            self.webview.clearHistory()
            self.webview.clearCache(True)
            self.webview.clearFormData()
            self.webview.destroy()
            #self.layout = None
            #self.webview = None
##########################################

##############using this draw #######################
    @run_on_ui_thread
    def draw(self,surface):
        #p=Point()
        #mActivity.getWindow().getWindowManager().getDefaultDisplay().getSize(p)
        canvas=surface.lockCanvas(None)#Rect(0,0,p.x,p.y))
        canvas.translate(-self.webview.getScrollX(), -self.webview.getScrollY())
        self.webview.draw(canvas)
        #canvas.restore()
        surface.unlockCanvasAndPost(canvas)
        #print('draw #########')




        
    @run_on_ui_thread
    def _size(self, size):
        if self.webview:
            params = self.webview.getLayoutParams()
            params.width,params.height = size
            self.webview.setLayoutParams(params)

    def pause(self):
        if self.webview:
            self.webview.pauseTimers()
            self.webview.onPause()

    def resume(self):
        if self.webview:
            self.webview.onResume()       
            self.webview.resumeTimers()

    def downloads_directory(self):
        # e.g. Android/data/org.test.myapp/files/Download
        dir_type = Environment.DIRECTORY_DOWNLOADS
        context =  PythonActivity.mActivity.getApplicationContext()
        directory = context.getExternalFilesDir(dir_type)
        return str(directory.getPath())

###################################below code i am using 
    @run_on_ui_thread
    def _back_pressed(self):
        if self.webview.canGoBack():
            self.webview.goBack()
        else:
            print("Webview can't go back!")
            #self.dismiss()  
        return True
    @run_on_ui_thread
    def load_url(self,url):
        self.webview.loadUrl(url)



#### Touch Implementations 
    def touch_down(self,x,y,wid):
        originalDownTime = SystemClock.uptimeMillis()
        eventTime = SystemClock.uptimeMillis() 
        x=x-wid.pos[0]
        #print("@@@@",wid.pos)
        y=((wid.height)-(y-wid.pos[1]))
        metaState = 0
        motionEvent = MotionEvent.obtain(originalDownTime,eventTime,MotionEvent.ACTION_DOWN,x,y,metaState)
        returnVal = self.webview.dispatchTouchEvent(motionEvent)
        #print('Dispached touch down in java ',returnVal)

    
    def touch_move(self,x,y,wid):
        originalDownTime = SystemClock.uptimeMillis()
        eventTime = SystemClock.uptimeMillis() 
        x=x-wid.pos[0]
        y=((wid.height)-(y-wid.pos[1]))
        #print(self.metric.widthPixels,self.metric.heightPixels,)
        metaState = 0
        motionEvent = MotionEvent.obtain(originalDownTime,eventTime,MotionEvent.ACTION_MOVE,x,y,metaState)
        returnVal = self.webview.dispatchTouchEvent(motionEvent)
        #print('Dispached touch move in java ',returnVal)

    def touch_up(self,x,y,wid):
        originalDownTime = SystemClock.uptimeMillis()
        eventTime = SystemClock.uptimeMillis() 
        x=x-wid.pos[0]
        y=((wid.height)-(y-wid.pos[1]))
        metaState = 0
        motionEvent = MotionEvent.obtain(originalDownTime,eventTime,MotionEvent.ACTION_UP,x,y,metaState)
        returnVal = self.webview.dispatchTouchEvent(motionEvent)
        #print('Dispached touch up in java ',returnVal)
        #print('screen size == ',get_screen_size())






def get_screen_size():
    displayMetrics = mActivity.getContext().getResources().getDisplayMetrics()
    return displayMetrics.widthPixels,displayMetrics.heightPixels

def get_fullScreen_height():
    context=mActivity.getContext()
    displayMetrics = context.getResources().getDisplayMetrics()
    windowManager = context.getSystemService(Context.WINDOW_SERVICE)
    windowManager.getDefaultDisplay().getRealMetrics(displayMetrics)
    return displayMetrics.heightPixels



@run_on_ui_thread
def immersive_mode(status='enable'):
    window = mActivity.getWindow()
    from kvdroid.jclass.android import View
    View = View()
    if status == "disable":
        return window.getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
            | View.SYSTEM_UI_FLAG_VISIBLE)
    else:
        return window.getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY)


