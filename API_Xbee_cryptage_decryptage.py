import serial
import time

#Toues les adresses des XBee ont les memes 6 premiers bits, seuls les 2 derniers changes 
#00 13 A2 00 41 6A est une partie commune a TOUTES les XBess
base_adresses = ['00','13','A2','00','41','6A']
#"Annuaire" de l'utilisateur
liste_adresses = [['johann1','8A','22'],['johann2','89','6B'],['coco1','8B','26']]
#Saut d'une ligne (presentation)
print('')
#Choix du port (les ports sur Linux sont notes /dev/ttyUSB*)
SERIAL_NUM = input("Numero du port : ")
SERIAL_PORT = '/dev/ttyUSB'+SERIAL_NUM
#Ecrit en couleur sur quel port l'utilisateur se trouve
print('\033[33mVous êtes sur le port',SERIAL_PORT,'\n\033[37m')
#Baud Rate
SERIAL_RATE = 9600

ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)

#Cette fonction genere des adresses entieres a partir de la liste d'adresse et de la base
def generer_adresses():
    liste_adresses_entiere=[]
    #Construction des adresses entieres, et stockage dans une liste
    for i in liste_adresses:
        liste_adresses_entiere.append(base_adresses+i[1:])
    
    #Affichage pour l'utilisateur des adresses disponible dans l'annuaire
    print('Adresses disponibles : ')
    for i in range (0,len(liste_adresses)):
        print('     Adresse',i,':',liste_adresses[i][0],'(',liste_adresses[i][1],liste_adresses[i][2],')')
    
    return liste_adresses_entiere

#Cette fonction permet de convertir un nombre base 10 en str hexadecimal (ex : 15 = '0F')
def int_to_hex(nr):
  h = format(int(nr), 'x')
  return '0' + h if len(h) % 2 else h

#Cette fonction genere la trame en fonction de l'adresse du destinataire et du message
def creationtrame(adresse_destination, message_ascii):
    trame = []
    
    #Les parametres start_delimiter, frame_type, frame_id et option ne changent pas 
    start_delimiter = '7E'

    frame_type = '00'

    frame_id = '01'

    dest_adress = adresse_destination

    option = '00'
    
    #Convertion du message en hexadecimal (ex : hey = [104,101,121] = ['68','65','79'])
    RF_data = []
    for i in message_ascii:
        RF_data.append(int_to_hex(i))

    #Calcul de la taille, stockee sur 2 bits, taille = 11 + nombres de caracteres message
    length = int_to_hex(str(11 + len(message_ascii)))
    
    #On ajoute un bit = 0 si la longeur ne fait qu'un bit
    if len(length)<4:
        length = ['00',length]
    else:
        length = [length[0:1],length[2:3]]
    
    #On ajoute tous ces parametres a la trame
    trame.append(start_delimiter)
    for i in length:
        trame.append(i)
    trame.append(frame_type)
    trame.append(frame_id)
    for i in dest_adress:
        trame.append(i)
    trame.append(option)
    for i in RF_data:
        trame.append(i)

    #Calcul du checksum
    checksum = 0
    for i in trame[3:]:
      checksum = checksum + (int(i, 16))
    
    checksum = int_to_hex(checksum)
    
    if len(checksum)>2:
      checksum = checksum[len(checksum)-2:]

    checksum = (int('FF', 16)) - (int(checksum, 16))
    checksum = int_to_hex(checksum)

    trame.append(checksum)

    return trame

def reception_avec_decryptage():
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

    #Retrait des "parasites" au debut du message
    message_r = message_r[8:len(message_r)-1]

    #On affiche le message recu
    for i in message_r:
        message_sortie = message_sortie + i
    print(message_sortie)

def reception_sans_decryptage():
    
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

            #On recupere le caractère recu (la communication se fait bit par bit)
            data_r = ser.read()
            message_r.append(data_r[0])
        
        #Si jamais le delais d'une seconde est depasse, on sort de la boucle
        #Cela veut dire qu'on a recu l'integralite du message car chacun des
        #bit est envoye a la suite, en moins d'une seconde
        if time.time() > timeout_start + timeout:
            break
    
    #Retrait des "parasites" au debut du message
    message_r = message_r[8:len(message_r)-1]

    #On affiche le message recu
    for i in message_r:
        message_sortie = message_sortie + chr(i)
    print(message_sortie)

def cryptage(message):
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
    
    return message_crypte

def convertion_ascii(message):
    #On converti le message en ascii
    message_ascii = []
    for i in message:
            i=ord(i)
            message_ascii.append(i)
    
    return message_ascii

#On demande a l'utilisateur ce qu'il souhaite, et en fonction certaines fonctions sont executes
cryptage_ouinon = input('Utilisation du cryptage ? (oui ou non) : ')
print('')
mode = int(input('Envoi ou recevoir ? (0 ou 1) : '))
print('')

while True:

    if cryptage_ouinon == 'oui':

        if mode == 1:

            reception_avec_decryptage()
            
        if mode == 0:
            
            #Generation des adresses
            liste_adresses_dispos = generer_adresses()
            choix_destinataire = int(input("A qui envoyer ? (numéro de l'adresse) : "))
            print('')
            
            #Demande du message a l'utilisateur
            message = input('rentrer le message : ')
            print('')
            
            destinataire = liste_adresses_dispos[choix_destinataire]
            
            #Cryptage
            message_converti = cryptage(message)
            #Trame
            trame = creationtrame(destinataire, message_converti)
            trame_convertie = []

            #Convertion de la trame en nombres
            for i in trame:
                trame_convertie.append(int(i,16))
            
            ser.write(trame_convertie)
            print('\033[36m-----------------\nMESSAGE ENVOYE\n-----------------\n\033[37m')
    
    if cryptage_ouinon == 'non':

        if mode == 1:

            reception_sans_decryptage()
            
        if mode == 0:
            
            #Generation des adresses
            liste_adresses_dispos = generer_adresses()
            choix_destinataire = int(input("A qui envoyer ? (numéro de l'adresse) : "))
            print('')

            #Demande du message a l'utilisateur
            message = input('rentrer le message : ')
            print('')
            
            destinataire = liste_adresses_dispos[choix_destinataire]

            #Cryptage
            message_converti = convertion_ascii(message)

            #Trame
            trame = creationtrame(destinataire, message_converti)
            trame_convertie = []

            #Convertion de la trame en nombres
            for i in trame:
                trame_convertie.append(int(i,16))
            
            ser.write(trame_convertie)
            print('\033[36m-----------------\nMESSAGE ENVOYE\n-----------------\n\033[37m')
        
