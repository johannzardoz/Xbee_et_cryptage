import pygame
import pygame_menu
import serial
import time

#Toues les adresses des XBee ont les memes 6 premiers bits, seuls les 2 derniers changes 
#00 13 A2 00 41 6A est une partie commune a TOUTES les XBess
base_adresses = ['00','13','A2','00','41','6A']
#"Annuaire" de l'utilisateur
liste_adresses = [['johann1','8A','22'],['johann2','89','6B'],['dorian1','8A','0C'],['dorian2','8B','2F']]

#Cette fonction genere des adresses entieres a partir de la liste d'adresse et de la base
def generer_adresses():
    list_dispos = []
    liste_adresses_entiere=[]
    #Construction des adresses entieres, et stockage dans une liste
    for i in liste_adresses:
        liste_adresses_entiere.append(base_adresses+i[1:])
    
    #Affichage pour l'utilisateur des adresses disponible dans l'annuaire
    for i in range (0,len(liste_adresses)):
        list_dispos.append(liste_adresses[i][0]+' ('+liste_adresses[i][1]+' '+liste_adresses[i][2]+')')
    
    return liste_adresses_entiere, list_dispos

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

#Cette fonction sert a definir le parametre choisi par l'utilisateur dans l'interface
def choix_port(a,b):
    global SERIAL_NUM
    SERIAL_NUM = b
    print('choix du port')

#Cette fonction sert a definir le parametre choisi par l'utilisateur dans l'interface
def choix_cryptage(a,b):
    global cryptage_ouinon
    cryptage_ouinon = b
    print('choix du cryptage', b)

#Cette fonction sert a definir le parametre choisi par l'utilisateur dans l'interface
def choix_mode(a,b):
    global mode
    mode = b
    print('choix du mode', b)

#Cette fonction sert a definir le parametre choisi par l'utilisateur dans l'interface
def text_input(a):
    global message
    message = a
    print('message rentre')

#Cette fonction sert a definir le parametre choisi par l'utilisateur dans l'interface
def choix_destinataire(a,b):
    global destinataire
    destinataire = liste_adresses_entiere[b]
    print('choix du destinataire')

#Cette fonction se lance quand l'utilisateur clique sur "Envoi, ou mise en mode reception" dans l'interface
def lancement():

    #Baud Rate
    SERIAL_RATE = 9600
    #Choix du port (les ports sur Linux sont notes /dev/ttyUSB*)
    SERIAL_PORT = '/dev/ttyUSB'+str(SERIAL_NUM)

    ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)
    
    #En fonction des choix des fonctions sont executes
    while True:

        if cryptage_ouinon == 1:

            if mode == 1:
            #---PROGRAMME DE RECEPTION CRYPTE---
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

                for i in message_r:
                    message_sortie = message_sortie + i

                #Affichage du message sur le terminal (control des bugs)
                print(message_sortie) 
                #Affichage du message dans l'interface
                menu.clear(reset=False)
                menu.add_label("******************************")
                menu.add_label("Message reçu :")
                menu.add_label(message_sortie)
                menu.add_label("******************************")
                menu.mainloop(surface, disable_loop=True)
                    
            if mode == 0:
                    
                message_converti = cryptage(message)
                trame = creationtrame(destinataire, message_converti)
                trame_convertie = []

                for i in trame:
                    trame_convertie.append(int(i,16))
                    
                ser.write(trame_convertie)
                print(trame_convertie)
                print('\033[36m-----------------\nMESSAGE ENVOYE\n-----------------\n\033[37m')

                break
            
        if cryptage_ouinon == 0:

            if mode == 1:
            #---PROGRAMME DE RECEPTION NON CRYPTE---

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

                for i in message_r:
                    message_sortie = message_sortie + chr(i)
                
                #Affichage du message sur le terminal (control des bugs)
                print(message_sortie) 
                #Affichage du message dans l'interface
                menu.clear(reset=False)
                menu.add_label("******************************")
                menu.add_label("Message reçu :")
                menu.add_label(message_sortie)
                menu.add_label("******************************")
                menu.mainloop(surface, disable_loop=True)
                    
            if mode == 0:

                message_converti = convertion_ascii(message)
                trame = creationtrame(destinataire, message_converti)
                    
                trame_convertie = []
                for i in trame:
                    trame_convertie.append(int(i,16))
                
                print(trame)
                ser.write(trame_convertie)
                print('\033[36m-----------------\nMESSAGE ENVOYE\n-----------------\n\033[37m')

                break

cryptage_ouinon = None
mode = None
SERIAL_NUM = 0
message = ''
message_sortie = ''

liste_adresses_entiere,list_dispos = generer_adresses()

#Initialisation de pygame
pygame.init()

#Parametres du menu
surface = pygame.display.set_mode((800, 600))
menu = pygame_menu.Menu(600, 800, 'Interface de communication XBee', theme=pygame_menu.themes.THEME_DARK)

#Ajout des differents choix de parametres et boutons de l'interface
menu.add_selector('Port : ', [('', 9), ('0',0), ('1',1), ('2',2), ('3',3), ('4',4)], onchange=choix_port)
menu.add_selector('Cryptage : ', [('', 2), ('Oui',1), ('Non',0)], onchange=choix_cryptage)
menu.add_selector('Mode : ', [('', 2), ('Reception',1), ('Envoi',0)], onchange=choix_mode)
menu.add_label("******************************\nChoix des paramètres d'envoi (si necessaire)")
menu.add_text_input('Message a envoyer : ', default='', onreturn=text_input)
menu.add_selector('Destinataire : ', [('', 9), (list_dispos[0], 0), (list_dispos[1], 1), (list_dispos[2], 2),], onchange=choix_destinataire)
menu.add_label("******************************")
menu.add_button('Envoi, ou mise en mode reception', lancement)
menu.add_button('Quit', pygame_menu.events.EXIT)

menu.mainloop(surface)

