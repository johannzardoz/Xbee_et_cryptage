#include <SoftwareSerial.h>
#include <string.h>
#include <math.h>
SoftwareSerial xbee(2, 3);

int cle_priv_0 = 51;
int cle_priv_1 = 145;

void setup()
{
    xbee.begin(9600);                 
    Serial.begin(9600);
}
void loop()
{
  if(xbee.available()) {
    String caractere = "";
    String message = "";
    int caractere_dechifre;
    while(xbee.available())  {
      char crypted_data = xbee.read();
      if (crypted_data != ' '){
        caractere = String(caractere + crypted_data);
      }
      else{
        int code_carac=caractere.toInt();
        long long code_carac_pow=code_carac;
        int power=0;
        while (power<=cle_priv_0){
          code_carac_pow = code_carac_pow * code_carac;
          power = power + 1;
        }
        Serial.println(code_carac_pow);
        caractere_dechifre = code_carac_pow % cle_priv_1;
        //Serial.println(caractere_dechifre);
        caractere = "";
        }
      }
    }
}
