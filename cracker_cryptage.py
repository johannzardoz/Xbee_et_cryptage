message = [9135, 2186, 9864, 9135, 2186, 9864]
message_sortie = ''

while True:

  for i in range (1000,50000):
    d = i
    test = True
    print(d)

    for j in range (1000,50000):
      n = j
      for k in message:
        if (k ** i) % j >= 255:
          test = False
      
      if test != False:
        break
    if test != False:
      break
  if test != False:
    break

print ("clé privée : ", d,',',n)

for l in message:
  caractere_sortie = (l ** d) % n
  caractere_sortie = chr(caractere_sortie)
  message_sortie = message_sortie + caractere_sortie

print(message_sortie)