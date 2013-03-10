
try: import tempfile, wave, subprocess, os, signal, struct
except: 
    print("E: sound4python is unable to import a combination of %s"%
            ("tempfile, wave, subprocess, os, signal, struct"))

FNULL = open(os.devnull,'w')
def launchWithoutConsole(args,output=False):
    """Launches args windowless and waits until finished"""
    startupinfo = None
    if( 'STARTUPINFO' in dir(subprocess) ):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    if( output ):
        return subprocess.Popen(args, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,startupinfo=startupinfo, )
    else:
        return subprocess.Popen(args, stdin=subprocess.PIPE,
                stdout=FNULL ,stderr=FNULL, startupinfo=startupinfo)
 
# sound4python
def sound(itr,samprate=16000,autoscale=True,output=False):
    try: import numpy as np; foundNumpy=True;
    except: 
        foundNumpy=False;
        return None

    #for now, assume 1-D iterable
    mult = 1
    if( autoscale ):
        mult = 32768.0 / max(itr)
        #mult = 128.0 / max(itr)

    #create file in memory
    #with tempfile.SpooledTemporaryFile() as memFile:
    memFile = tempfile.SpooledTemporaryFile()
    if(True):
        waveWrite = wave.open(memFile,'wb')
        waveWrite.setsampwidth(2)        # int16 default
        waveWrite.setnchannels(1)        # mono  default
        waveWrite.setframerate(samprate) # 8kHz  default
        
        wroteFrames=False
        if( foundNumpy ):
            if( type(itr)==np.array ):
                if( itr.ndim == 1 or itr.shape.count(1) == itr.ndim - 1 ):
                    waveWrite.writeframes( (mult*itr.flatten()).astype(np.int16).tostring() )
                    wroteFrames=True
            else: #we have np, but the iterable isn't a vector
                waveWrite.writeframes( (mult*np.array(itr)).astype(np.int16).tostring() )
                wroteFrames=True
        if( not wroteFrames and not foundNumpy ):
            #python w/o np doesn't have short/int16, "@h" is "native,aligned short"
            waveWrite.writeframes( struct.pack(len(itr)*"@h",[int(mult*itm) for  itm in itr]) )
            wroteFrames=True
            
        if( not wroteFrames ):
            print("E: Unable to create sound.  Only 1D numpy arrays and numerical lists are supported.")
            return None

        memFile.seek(0) #configure the file object, memFile, as if we're just starting to read it

        try:
            # getting here means wroteFrames == True
            print("\nAttempting to play a mono audio stream of length")
            print("  %.2f seconds (%.3f thousand samples at sample rate of %.3f kHz)"%
                    ( 1.0*len(itr)/samprate , len(itr)/1000. , int(samprate)/1000.) )
            p=launchWithoutConsole(['sox','-','-d'])
        except: 
            print("E: Unable to launch sox.")
            print("E: Please ensure that sox is installed and on the path.")
            print("E: Try 'sox -h' to test sox installation.")
            waveWrite.close()
            return None

        try: 
            p.communicate(memFile.read())
            p.wait()
        except: 
            print("E: Unable to send in-memory wave file to stdin of sox subprocess.")
            waveWrite.close()
            return None
        #os.kill(p.pid,signal.CTRL_C_EVENT)
    #print memFile.closed #deletes temporary file in RAM
#end def sound(itr,samprate=8000,autoscale=True)
        






