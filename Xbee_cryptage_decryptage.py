import serial
import time

#Choix du port (les ports sur Linux sont notes /dev/ttyUSB*)
SERIAL_NUM = input("Numero du port : ")
SERIAL_PORT = '/dev/ttyUSB'+SERIAL_NUM
print(SERIAL_PORT)
#Baud Rate
SERIAL_RATE = 9600

ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)

def reception():
    #Cette fonction connait la cle privee (mais pas la publique)
    cle_priv = [51, 145]
    message_r = []
    message_sortie = ''

    #time.time() renvoit le temps écoulé depuis très longtemps, ce nombre permet d'être "au dessus" 
    #de celui renvoyé par time.time() pour ne pas directement sortir de la boucle
    timeout_start = 100000000000000000000000000000

    while True:
        #Le delais est regle sur 1 seconde
        timeout = 1 #seconds

        #On attend de recevoir quelque chose
        n = ser.inWaiting()
        if n :
            #On demarre le timer
            timeout_start = time.time()

            #On recupere et decrypte le caractère recu (la communication se fait bit par bit)
            data_r = ser.read()
            caractere_d = (int(data_r[0]) ** cle_priv[0]) % cle_priv[1]
            caractere_no_ascii = chr(caractere_d)
            message_r.append(caractere_no_ascii)
        
        #Si jamais le delais d'une seconde est depasse, on sort de la boucle
        #Cela veut dire qu'on a recu l'integralite du message car chacun des
        #bit est envoye a la suite, en moins d'une seconde
        if time.time() > timeout_start + timeout:
            break
    
    #On affiche le message recu
    for i in message_r:
        message_sortie = message_sortie + i
    print(message_sortie)

def cryptage_et_envoi(message):
    #Cette fonction connait la cle publique (mais pas la privee)
    cle_pub = [11, 145]
    
    #On converti le message en ascii
    message_ascii = []
    for i in message:
            i=ord(i)
            message_ascii.append(i)

    #Chaque caractere est crypte
    message_crypte = []
    for i in message_ascii:
        caractere_crypte = (i ** cle_pub[0]) % cle_pub[1]
        message_crypte.append(caractere_crypte)
    
    #Envoi du message
    ser.write(message_crypte)

#---------------------------------------------------------------#
while True:
    
    #L'utilisateur choisi le monde
    mode = int(input('Envoi ou recevoir ? (0 ou 1) : '))

    if mode == 1:

        reception()
            
    if mode == 0:

        message = input('rentrer le message : ')
        cryptage_et_envoi(message)
        