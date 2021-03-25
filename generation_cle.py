import random

def RSA():
    #Variables de bases
    max = int(input('Les nombres premiers choisis seront < à : '))
    premier = []
    e_possible = []

    #création d'une liste de nombre premier
    for i in range(2,max):
        non_premier = False
        for j in range(2,i):
            if i%j == 0:
                non_premier = True
        if non_premier == False:
            premier.append(i)

    #Tant qu'il n'a pas trouvé d, il boucle
    d_find = False
    while d_find == False:
        d = 0
        #prise de valeurs random différentes
        p = 0
        q = 0
        while p == q:
            p = random.choice(premier)
            q = random.choice(premier)

        n = p * q
        fi = (p-1)*(q-1)

        while e_possible == []:
            for i in range (2,fi):
                if fi%j != 0:
                    e_possible.append(i)

        e = random.choice(e_possible)

        while (e * d % fi) != 1:
            d += 1
            if d > 50000:
                break

        if (e * d % fi) == 1:
            d_find = True
    
    cle_publique = [e,n]
    cle_privee = [d,n]

    return cle_publique,cle_privee

cle_pub,cle_priv = RSA()

print('cle_pub : ',cle_pub, 'cle_priv : ',cle_priv)