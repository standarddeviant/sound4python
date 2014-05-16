try: import tempfile, wave, subprocess, os, signal, struct
except: 
    print("E: sound4python is unable to import a combination of %s"%
            ("tempfile, wave, subprocess, os, signal, struct"))

    
import threading
import scipy.io.wavfile
import numpy as np
import datetime as dt
    

class Sound4Python(object):
    def __init__(self):
        self.seekSec = 0
        self.FNULL = open(os.devnull,'w')
        
    def launchWithoutConsole(self, args,output=False):
        """Launches args windowless and waits until finished"""
        startupinfo = None
        if 'STARTUPINFO' in dir(subprocess):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if output:
            return subprocess.Popen(args, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,startupinfo=startupinfo, )
        else:
            return subprocess.Popen(args, stdin=subprocess.PIPE,
                    stdout=self.FNULL ,stderr=self.FNULL, startupinfo=startupinfo)
        
    def createMemfile(self, itr,samprate=16000,autoscale=True,output=False):
        try: import numpy as np; foundNumpy=True;
        except: 
            foundNumpy=False;
            
        self.itr = itr
        self.samprate = samprate
    
        #for now, assume 1-D iterable
        mult = 1
        if autoscale:
            mult = 32768.0 / max(itr)
            #mult = 128.0 / max(itr)
    
        #create file in memory
        #with tempfile.SpooledTemporaryFile() as memFile:
        self.memFile = tempfile.SpooledTemporaryFile()
    
        #create wave write objection pointing to memFile
        self.waveWrite = wave.open(self.memFile,'wb')
        self.waveWrite.setsampwidth(2)        # int16 default
        self.waveWrite.setnchannels(1)        # mono  default
        self.waveWrite.setframerate(samprate) # 8kHz  default
        
        wroteFrames=False
        #Let's try to create sound from NumPy vector
        if foundNumpy :
            if type(itr)==np.array:
                if( itr.ndim == 1 or itr.shape.count(1) == itr.ndim - 1 ):
                    self.waveWrite.writeframes( (mult*itr.flatten()).astype(np.int16).tostring() )
                    wroteFrames=True
            else: #we have np, but the iterable isn't a vector
                self.waveWrite.writeframes( (mult*np.array(itr)).astype(np.int16).tostring() )
                wroteFrames=True
        if not wroteFrames and not foundNumpy:
            #python w/o np doesn't have "short"/"int16", "@h" is "native,aligned short"
            self.waveWrite.writeframes( struct.pack(len(itr)*"@h",[int(mult*itm) for  itm in itr]) )
            wroteFrames=True
            
        if not wroteFrames:
            print("E: Unable to create sound.  Only 1D numpy arrays and numerical lists are supported.")
            self.waveWrite.close()
            return None
    
        
    def play(self):                 
        #configure the file object, memFile, as if it has just been opened for reading
        self.memFile.seek(0)
        try:
        # getting here means wroteFrames == True
            print("\nAttempting to play a mono audio stream of length")
            print("  %.2f seconds (%.3f thousand samples at sample rate of %.3f kHz)"%
                    ( 1.0*len(self.itr)/self.samprate , len(self.itr)/1000. , int(self.samprate)/1000.) )
            self.p=self.launchWithoutConsole(['sox','-','-d'])
        except: 
            print("E: Unable to launch sox.")
            print("E: Please ensure that sox is installed and on the path.")
            print("E: Try 'sox -h' to test sox installation.")
            self.waveWrite.close()
            return None
    
        self.startTime = dt.datetime.now()
        try:
            self.p.communicate(self.memFile.read())   
            self.p.wait()
        except: 
            print("E: Unable to send in-memory wave file to stdin of sox subprocess.")
            self.waveWrite.close()
            return None

    def seek(self, sec):
        sr = self.wav[0]
        idx = np.floor(sec * sr)
        if idx > self.wav[1].shape[0]:
            raise ValueError("tried to seek outside of wav length")
            
        self.seekSec = sec
            
        self.createMemfile(self.wav[1][idx:,0], self.wav[0]) 
        
        
    def loadWav(self, wavPath=None):
        if wavPath is not None:
            self.wavPath = wavPath
            
        self.wav = scipy.io.wavfile.read(self.wavPath)
        self.seekSec = 0
        self.createMemfile(self.wav[1][:,0], self.wav[0]) 
        
        
    def playInThread(self):
        self.wt = Sound4PythonThread(self)
        self.wt.Run()        
        
    def terminateProcess(self):
        try:
            self.p.terminate()
        except OSError, e:
            if str(e) == "[Errno 3] No such process":
                pass
            else:
                raise e          
        
        
    def stop(self):
        self.terminateProcess()
        self.seek(0)
        
    def pause(self):
        self.stopTime = dt.datetime.now()
        self.terminateProcess()
        secDiff = (self.stopTime - self.startTime).total_seconds()
        self.seek(secDiff)
        
        
class Sound4PythonThread(threading.Thread):    
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent
    
    def run(self):
        self.parent.play()

    def Run(self):
        self.start()
