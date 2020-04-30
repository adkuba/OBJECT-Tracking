**Siec neuronowa**
Tworzymy siec ktora ma rozpoznawac czy obrazki sa podobne.
W creaty.py jest jak stworzyc od zera wlasna siec. Ja bede wykorzystywal mobilenet v2 poniewaz jest juz dobrze dopracwana.

mobilenet wielkosc input 224 x 224 czyli obrazki dwa wielkosci 
112 x 224

* Stworzyc do tego program ktory ulatwi nam tworzenie zestwu danych. Plik data.py DONE
* Zgromadzic dane, wczesniej wytenowac jeszcze raz object detector na konie??

Wiekszosc na podstawie mojego detektora konikow
Reszta na jakiejs bazie coco

**Wydajnosc** <br/>
v1 <br/>

NO - 1247 <br/>
YES - 1805 <br/>
train - 86% <br/>
validation - 72% <br/>
end - 63% <br/>
cross_entropy kiepskie (nie spada)

----
v2 <br/>

NO - 2434 <br/>
YES - 3028 <br/>
train - 73% <br/>
validation - 74% <br/>
end - 67%
cross_entropy takie samo

----
 
v3 <br/>
nie 075 tylko 140 NIC NIE DAJE

**MobilenetV2 jako feature extractor** <br/>

Usunac ostatnie warstwy z mobilenet aby po wrzuceniu obrazka wyrzucalo tylko wektor/tensor ktory bede mogl porownac z nastepnym. Plik features.py

Za pomoca kerasa latwo moge zdjac ostatnia warstwe z mobilenetv2. Teraz pominac zapis do pliku pb i urzywac kerasa to wyswietlenia wynikow. <br/>
Pozniej przekonwertowac z KERASA na PB (nie szukac czegos w stylu how to freeze graph). Znalezc dobra funkcje porownujaca uzyskane wektory.
Przeprowadzic test dla duzej liczby zdjec, Uporzadkowac features.py, reader.py zostawic, uzyje go pozniej, jak przekonwertuje na plik .pb

https://medium.com/@franky07724_57962/using-keras-pre-trained-models-for-feature-extraction-in-image-clustering-a142c6cdf5b1

https://www.dlology.com/blog/how-to-convert-trained-keras-model-to-tensorflow-and-make-prediction/

Do porownania roznic uzyc sumy roznic poszczegolnych elementow wyniku (manhattan distance)

----
**WYDAJNOSC** <br/>
z max pooling - wolno dziala 89% <br/>
z avg pooling - 88% (tak samo po najbardziej rozniacych sie wynikach) <br/>
bez pooling - 86% <br/>

TERAZ STWORZYC CALY MODEL <br/>
model ma dwa inputy - dwa obrazki, robimy concentrate wejscia dodajemy dense layer i szkolimy. zobaczyc jaka dokladnosc. <br/>

Dopracowac model, jesli bedzie dokladnosc wieksza niz 88% to bieremy. <br/>

Zmieniony image generator - teraz geneuje obrazki raz z jednego folderu raz z drugiego. <br/>

stworzyc kilka plikow dla roznych struktur modelu i pozniej wykonac ja w chmurze z zapisem do pliku. <br/>

sieci z wieksza iloscia neuronow z jedna dodatkowa warstwa dense wpadaly na dokladnosc 5527 i nie chcialy isc wyzej. <br/>
Reszta wynikow w pliku. <br/>

Wydaje sie ze jedna dodatkowa warstwa nie ma zupelnie sensu.
Dwie dodatkowe sa dobre przy wieszej ilosci neuronow - przetestowac z wieksza iloscia.
Trzy z mala iloscia na konicu sa kiepskie - przetestowac z wieksza iloscia.

-----

PRZETESTOWAC JESZCZE JEDNA WARSTWE z 640 neuronami plus model z 4 dodatkowymi warstwami 1000-800-600-400 i model z 3 z wieksza iloscia 1000-800-600
<br/>
WYTRENOWAC DO KONCA MODEL 3_1000_800_600 <br/>
pozniej 2-960-640 <br/>

Kiepskie wyniki nadal, zrobic fine tune modelu 3_1000_800_600_continue <br/>
mozna jeszcze raz wytrenowac jeden z modeli z jeszcze lepiej pomieszanymi danymi <br/>

TERAZ dobry wynik usyskala siec 1_640 z fine tuning
ZGROMADZIC WIECEJ DANYCH, zrobic tak zeby siec ladowala wektor i obrazek a nie dwa obrazki wytrenowac jeszcze raz <br/>
NAWAZNEIJSZE PLIKI: data.py / model_saver.py / caly folder google cloud
ZROBIC dwa warianty sledzenia obrazkow: pierwszy - matematyczna suma roznic drugi moja siec neuronowa
W jednym pliku FINAL.PY 

-----

No tak srednio bym powedzial to dziala, moze wiecej danych do mojej sieci???
raczej dobra droga jest jeszcze jedna siec neuronowa niz porownanie roznicy <br/>

MUSZE OSIAGNAC POWYZEJ 90% dokladnosci!

WIECEJ ZDJ OCZYSCIC DANE 

W cloud train 15 mam warstwe dense przed global avarage pooling

w 16 mam flatten

skonczylem oczyszczec zdjecia na yes 688, sprobowac usunac/przeniesc zdj gdzie obiektty sie nakladaja (do NO) zeby jakos to odroznic
rowniez moj detektor powienien dzialac o wiele lepiej

Po tych testach wybrac 3 najlepsze sieci i zgromacic wiecej danych KONIEC!
------

A MOZE IMAGE SEGMANETATION <br/>
najlepsze sieci:
* 1_640                 84%
* 0                     78% to powinno dobrze zadzialac
* 1_1280_combined       81%
* dense 640 przed avg   79%
* 2_960_640             idk mozna sprawdzic jedna z lepszych u mnie

<br/>
teraz sledzic auta zeby sprawdzic koncept