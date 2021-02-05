# Adresse USBTMC du Teledyn Lecroy Wavesurfer 3022
# VISA_ADDRESS = "USBTMC:USB0::0x05FF::0x1023::LCRY0120N12304::INSTR"[7:]

# probleme de connection ?
# http://alexforencich.com/wiki/en/python-usbtmc/readme

import usbtmc
import time
import numpy as np


"""
Quelques commandes/instructions pouvant être envoyé à l'oscillo
WAVESURFER 3022 pour intéraction.
La liste exhaustive peut-être trouvée à l'addresse suivante :

https://www.arc.ro/userfiles/docs/Teledyne%20LeCroy/Osciloscoape/Fisiere%20disponibile/Teledyne%20LeCroy%20WaveSurfer%203000%20Oscilloscopes%20-%20Automation%20Command%20Reference%20Manual.pdf

http://cdn.teledynelecroy.com/files/manuals/maui-remote-control-and-automation-manual.pdf
"""
# Command "Legacy"
lgc_ArmWait = "ARM;WAIT"
lgc_TraceSt = 'C{}:TRACE {}' # ON, OFF
lgc_HeadOff = "COMM_HEADER {}" # ON, OFF
lgc_TrigMod = 'TRIG_MODE {}' # NORMAL, AUTO, SINGLE, STOP
lgc_Setup   = 'WAVEFORM_SETUP?'
# Command Visual Basic
vbs_TrigMod = 'app.acquisition.triggermode'
vbs_TchScrn = 'app.TouchScreenEnable'
vbs_HorScal = 'app.Acquisition.Horizontal.HorScale'
vbs_ChXBdWd = 'app.Acquisition.C{}.BandwidthLimit'
vbs_ChXCoup = 'app.Acquisition.C{}.Coupling'
vbs_ShoMeas = 'app.measure.showmeasure'
vbs_ClearAl = 'app.measure.clearall'
vbs_ClearSw = 'app.measure.clearsweeps'
vbs_TrigLvl = 'app.Acquisition.trigger.edge.level'
vbs_Default = 'app.settodefaultsetup'
vbs_OutScal = 'Join(app.Acquisition.C{}.Out.Result.DataArray({}),"{}")'


def save_signal_to_file(list_of_array, filename, header='', channel=1):
    timestamp = time.localtime()
    head  = "LECROYWS3022,12304,Waveform\n"
    head += "channel:"+str(channel)+"\n"
    head += "date:"+time.strftime(format("%d %b %Y"),timestamp)+"\n"
    head += "time:"+time.strftime(format("%H:%M:%S"),timestamp)+"\n"
    head += header
    np.savetxt(filename, np.transpose(list_of_array), fmt="%.2e, %.5e", delimiter=',', header=head, newline='\r\n', comments='')
    
class Scope(object):
    """
    """

    def __init__(self, connection='usb'):
        """
        Initialisation de la classe.
        
        ----------
        
        connection : str
            Chaîne de caractères définissant le type de connection.
            Pour l'instant seul 'usb' est supporté.
        """
        self.connection = connection
        self.inst = None
        self.trigger = 'normal'
        self.trigger_lvl = 0
        self.touchscreen = False
        self.horscale = None
        self.C1 = None
        self.C2 = None

    
    @property
    def trigger(self):
        return self.inst.ask("TRIG_MODE?")
        #return self.__trigger
    
    @trigger.setter
    def trigger(self, val):
        if self.inst:
            #self.write(vbs_TrigMod + ' = "{}" ' . format(val))
            self.inst.write("TRIG_MODE {}" . format(val))
        self.__trigger = val

        
    @property
    def touchscreen(self):
        return self.__touchscreen
    
    @touchscreen.setter
    def touchscreen(self, val):
        if self.inst:
            self.write(vbs_TchScrn + ' = {} ' . format(val))
        self.__touchscreen = val

        
    @property
    def horscale(self):
        return self.__horscale
    
    @horscale.setter
    def horscale(self, val):
        if self.inst:
            self.write(vbs_HorScal + ' = {} ' . format(val))
        self.__horscale = val
    
    def default(self):
        list_default = (
            # Sparing (SP=0: send all data points)
            # Number of points (NP=0: send all data points)
            # First point (FP=0)
            # Segment Number (SN=0: all segments)
            "WAVEFORM_SETUP SP,0,NP,0,FP,0,SN,0",
            # Encoding Block format DEF9
            # Data Type WORD (16-bit)
            # Encodig BIN
            "COMM_FORMAT DEF9,WORD,BIN",
            # LSB first
            "COMM_ORDER LO")
        [ self.inst.write(u) for u in list_default ]

        
    def connect(self, address=None):
        """
        Méthode pour établir la connection avec l'oscillo. Si la
        connection est établie, la fonction renvoie l'identité
        de l'oscilloscope.

        ----------

        address : str
            Chaîne de caractères contenant l'addresse VISA de
            l'instrument.
            
        ----------
        
        st : bool
            'True' ou 'False' selon la résolution de la connection.
        """
        if self.connection == 'usb':
            print(usbtmc.list_devices())
            self.inst = usbtmc.Instrument(address)
            try:
                print(self.inst.ask('*IDN?'))
            except:
                print('Connection failed.')
                self.inst = False
            else:
                print('Connection succeed.')


    def write(self, vbs_command):
        """
        Ecrit une commande visa dans l'instance de instrument.

        ----------

        instance : instance usbtmc/visa
            Instance de l'instrument généré par usbtmc.

        vbs_command : str
            Chaîne de caractère contenant la command visual basic.
            
        """
        cmd = r"""vbs {} """.format(vbs_command)
        self.inst.write(cmd)
        
    def read(self, vbs_command):
        """
        Lit le résultat d'une commande visa dans l'instance.

        ----------

        vbs_command : str
            Chaîne de caractère contenant la command visual basic.

        """
        return self.inst.ask(r"""vbs? 'return={}' """ . format(vbs_command))
    
    
    def get_waveform(self, channel):
        """
        Lecture du signal de la voie choisie.
        
        ----------
        
        channel : int
            Numéro de la voie à lire.
            
        ----------
       
        return : (array, array)
            Tuple contenant l'amplitude et le temps des échantillons.
            
        """
        sep = ';'
        cmd = vbs_OutScal.format(channel, 1, sep)
        amp = []
        try:
            sig = self.read(cmd)[4:].split(sep)
        except:
            sig = [np.nan,]
        for i in sig :
            try:
                amp.append(float(i))
            except:
                amp.append(np.nan)
        amp = np.array(amp)
        
        # Lecture de la période d'échantillonage. Pour avoir toutes
        # infos : ask("C1:INSPECT? WAVEDESC")
        #Te = float(self.inst.ask("C{}:INSPECT? HORIZ_INTERVAL" . format(channel)).split(":")[-1][:-1].strip())
        cmd = "app.Acquisition.Horizontal.SamplingRate"
        Te = 1/float(self.read(cmd).split(' ')[-1])
        tim = [ t*Te for t in range(len(amp)) ]
        tim = np.array(tim)
                    
        return (tim, amp)
    

    def acquire(self, channel, sleep=0):
        """
        Réalise l'acquisition sur l'oscilloscope.
        
        ---------
        
        sleep : float
            Temps de pause entre l'auto-ajustement du gain
            verticale et l'acquisition en elle même.
            
        ---------
            
        return : array, array
            'Array' contenant l'amplitude et le temps des échantillons.
        
        """
        self.write('app.Acquisition.C1.FindScale ')
        time.sleep(sleep)

        self.trigger = 'stop'
        s = self.get_waveform(channel) #C1
        self.trigger = 'normal'

        return s[0], s[1]
    
    
    def template():
        print(self.inst.ask("TEMPLATE?"))
        
class Channel(Scope):
    """
    """
    def __init__(self, instance, channel, coupling="AC1M", bandwidth="20MHz"):
        """
        Initialisation de la classe.
        
        ----------

        instance : instance usbtmc/visa
            Instance de l'instrument généré par usbtmc.
            
        channel : str
            Numéro de la chaîne de l'oscilloscope
            
        coupling : str
            valeurs possible pour le wavesurfer 3022 "AC1M", "DC1M" ou "DC50"
            
        bandwidth : str
            valeurs possible pour le wavesurfer 3022 "Full", "20MHz"
        """
        self.__instance = instance
        self.channel = channel
        self.coupling = coupling
        self.bandwithlimit = bandwidth
        self.verscale = None
        # Affiche la trace temporelle de la chaine
        instance.inst.write(lgc_TraceSt . format(channel, 'ON') )

    @property
    def coupling(self):
        return self.__instance.read(vbs_ChXCoup.format(self.channel))
        #return self.__coupling

    @coupling.setter
    def coupling(self, val):
        cmd = vbs_ChXCoup.format(self.channel) + ' = "{}" '.format(val)
        self.__instance.write(cmd)
        self.__coupling = val

        
    @property
    def bandwithlimit(self):
        return self.__instance.read(vbs_ChXBdWd.format(self.channel))
        #return self.__bandwithlimit

    @bandwithlimit.setter
    def bandwithlimit(self, val):
        cmd = vbs_ChXBdWd.format(self.channel) + ' = "{}" '.format(val)
        self.__instance.write(cmd)
        self.__bandwithlimit = val