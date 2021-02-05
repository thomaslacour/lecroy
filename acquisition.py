import os
import time, timeit
import numpy
import numpy as np
import matplotlib.pyplot as plt

from scipy import signal as sg

import LeCroy3022
import misc

def signal_force(F_min, F_max, N_cycles, vitesse, M=4, plot=False, verbose=False):
    """
    Signal de force théoriquement reçu par la machine de traction lors
    de l'essai cyclique de compression/détente. Tous les paramètres de
    la fonction doivent être identiques aux paramètres de l'essai sur 
    la machine de traction.
    
    -------
    
    F_min : float
        Valeur minimale de la force lors de l'essai mécanique en Newton.
        
    F_max : float
        Valeur maximale de la force lors de l'essai mécanique en Newton.
        
    N_cycles : int
        Nombre de cycles compression/détente.
        
    vitesse : float
        Vitesse de chargement en (N/s).
        
    M : int
        Nombre de point sur un DEMI CYCLE.
        
    plot : bool
        Si 'True', affiche Force vs Temps et les points d'acquisition.
        
    verbose : bool
        Si 'True', affiche la liste des valeurs de force où doit être
        réalisée l'acquisition par l'oscilloscope.
        
    -------
    
    return : force, deltat, N
    
    force : lambda function
        Fonction F(t) permettant de renvoyer la force F en fonction du
        temps t.
        
    deltat : float
        Intervalle temporelle théorique entre deux acquisitions.
        
    N : int
        Nombre totale de points de mesure.
    
    """
    N_cycles = int(N_cycles)
    M = int(M)
    
    N = 2*N_cycles*(M) + 1 # nombre de point de mesure
    
    amp = F_max-F_min # amplitude des variations de force (N)
    Coeff = 2*N_cycles*amp/vitesse
    
    # fonction périodique triangulaire et positive
    force = lambda t : amp/2*(1 + sg.sawtooth(2*np.pi*N_cycles*t/Coeff, width=1/2)) + F_min
    
    deltat  = Coeff/(N-1)

    if plot:
        tem = np.linspace(0,1, 1001)*Coeff
        tem_a = np.linspace(0,Coeff,N,endpoint=True)
        plt.figure(figsize=(8,3))
        plt.plot(tem, force(tem))
        plt.plot(tem_a, force(tem_a), '.r', label='Point de mesure')
        plt.ylabel('Force (N)')
        plt.xlabel('Temps (s)')
        plt.legend()
        plt.show()
    if verbose:
        print(force(tem_a))
    
    return force, deltat, N


def save_estimated_force_to_file(list_of_array, filename, header='Force,Course,Temps'):
    """
    Sauvegarde le temps du script python auquel a été réalisé
    l'acquisition, ainsi qu'une ESTIMATION de la force déduite 
    de la vitesse de compression imposée sur la machine de 
    traction.
    
    -------
    
    list_of_array : list
        liste de <type 'numpy array'> contenant les quantités à
        enregistré dans le fichier texte.
    """
    timestamp = time.localtime()
    head  = "Force et temps estimés par le temps dand le script python\n"
    head += "La course est inconnue par python car contrôle en force !\n"
    head += "date:"+time.strftime(format("%d %b %Y"),timestamp)+"\n"
    head += "time:"+time.strftime(format("%H:%M:%S"),timestamp)+"\n"
    head += header
    np.savetxt(filename, np.transpose(list_of_array), 
               fmt="%.12e", delimiter=';', header=head, newline='\r\n', comments='')
    
    
def run(path, scope, channel, deltat, N_stop, countdown=10, force_fun=False):

    n = 1
    #signal = []
    time_acquisition = []
    force_estimate = []

    wait = 3.2 # seconds (wait for average sweeps and autocalibre)
    wait2 = 0

    print('\n\n\n');misc.countdown(int(countdown)) 

    t0 = tic = toc = timeit.default_timer()
    
    signal_filename = lambda i : "C{}__{}.txt".format(int(channel),str(i).zfill(5))
    
    t, x = np.zeros(100), np.zeros(100)
    
    while n <= N_stop:

        if (timeit.default_timer() + wait + wait2 - t0)/deltat < n-1 and n>1:
            time.sleep(deltat/100)
        else:

            try:
                t, x = scope.acquire(channel, sleep=wait)
            except:
                pass

            time_acquisition.append(timeit.default_timer()-t0)
            
            signal_path = os.path.join(path, signal_filename(n))

            LeCroy3022.save_signal_to_file( [t, x], signal_path, header="test" )

            if force_fun:
                #clear_output(wait=True)
                filename_force = path + ".txt"
                force_estimate.append( force_fun(time_acquisition[-1]) )
                tmp_list_array = [force_estimate, np.zeros(len(force_estimate)), time_acquisition]
                save_estimated_force_to_file(tmp_list_array, filename_force)
                print("{} : temps = {} (s) et force estimée = {} (N)".
                      format(n, np.round(time_acquisition[-1], decimals=2), np.round(force_estimate[-1]))
                )
                #wait2 = (force_estimate[0]-force_fun(0))/vF - wait
            else:
                print('Measure {} done at {} s'.format(n, np.round(time_acquisition[-1], decimals=2)) )
                
            wait2 = time_acquisition[0] - wait

            #except:
            #    pass


            n+=1

    return time_acquisition