# Setup
Zainstalowalem z oficjalnego repo unity ml-agents [poradnik](https://github.com/Unity-Technologies/ml-agents/blob/latest_release/docs/Readme.md) <br>
Pracuje na osobnym branchu ```git checkout -b UnityML_Testing``` <br>
Trzeba zaimportowac paczke ml-agents w nowym projekcie, przyklady sa w Projects/Assets/Examples z nich bede korzystal <br>
Przydatna komenda w vs code do auto formatowania kodu ```Ctrl + Shift + I```

# Unity environment
Opis srodowiska w unity do machine learning.
## Test version
Unity bedzie sterowalo kamera w osi Y, obserwacja (danymi wejsciowymi do sieci) bedzie obraz z kamery. <br>
Pusty obiekt GameController wybiera losowo przedmiot ktory bedzie sledzonym obiektem. Na podstawie sledzonego bedzie wyliczany wynik - odchylenie od srodka kamery, dazymy do jak najwiekszej nagrody - nagroda za wynik mniejszy niz 5 (kat), kara za wiekszy kat. Obiekty poruszaja sie losowo po planszy. Moze byc wiecej niz jeden obiekt z prefabu. [poradnik](https://github.com/Unity-Technologies/ml-agents/blob/latest_release/docs/Learning-Environment-Create-New.md) <br><br>

Uwagi:
* Nie dodaje funkcji add_sensors bo dodalem plik CameraSensor do kamery pod ktora jest podpiety agent [link](https://github.com/Unity-Technologies/ml-agents/blob/master/docs/Learning-Environment-Design-Agents.md).
* Max step to max ilosc krokow jakie moze wykonac agent w danym epizodzie, ja mam ustawione na 0 czyli nieograniczona liczba krokow bo sam zaprogramowalem ze epizod wylacza sie przy minucie dzialania. Dodatkowo nie moglem uzywac opcji heuristic only gdy mialem inna wartosc max step niz 0.
* Uwaga na plik config.yaml - wazne mozna sie dowiedziec wiecej co robia te parametry [link](https://github.com/Unity-Technologies/ml-agents/blob/master/docs/Training-ML-Agents.md)! Wazne u mnie byla wartosc max krokow uczenia oraz use recurrent: true - czyli agent ma pamiec i zapamietuje wczesniejsze dane [link](https://github.com/Unity-Technologies/ml-agents/blob/master/docs/Feature-Memory.md).
* Warto robic uczenie na kilku agentach na raz - moze zwiekszyc szybkosc uczenia.
* Fajne narzedzie do tensorboard - ngrok
* Uwaga na output sieci, zmienilem z Continous - output jako pojedynczy float, na Discrete - output jako tablica - do odpowiednich wartosci tablicy sa przypisane ruch w prawo, lewo, lub brak ruchu - analogicznie jak w przykladzie visual piramids [link](https://github.com/Unity-Technologies/ml-agents/blob/master/docs/Learning-Environment-Design-Agents.md). Dodatkowo w sumie nie wiem czy continous moze wyrzucac ujemne wartosci tak jak ja potrzebowalem - bo kamera zawsze skrecala w jedna strone, dlatego discrete bedzie lepsze chyba. dodatkowo recurrent lepiej pracuje z discrete a nie continous
* Opis wykresow na tensorboard [link](https://github.com/Unity-Technologies/ml-agents/blob/latest_release/docs/Using-Tensorboard.md).
* Std of reward to odchylenie standardowe - jak szeroko wartosci jakiejs wielkosci są rozrzucone wokol jej sredniej, mean to srenia.

## Notatki
przy training 5 wlaczylem uczenie z 1 agenta na 6 w kroku 480k, w training 8 zmniejszylem wielkosc kamery z 200 na 150 i output z continous na discrete, w training 4 mialem bardziej skomplikowane dawanie nagrody - zalezne od zmniejszajacego sie lub zwiekszajacego kata do obiektu plus mialem nastawione max steps co uniemozliwialo dluzsze sledzenie niz 100 krokow plus mialem w config.yaml max 500k krokow, w 5 dalem nagrode po prostu za celowanie w obiekt a kare w przeciwnym wypadku. w 8 byl stuck na 0 episode length wiec dodalem courisity [link](https://github.com/Unity-Technologies/ml-agents/blob/master/docs/Reward-Signals.md) - uczenie 10 plus zwiekszone buffer size i time, horizon, znowu wpadlo blisko zera teraz demo w uczeniu 

byl za duzy speed w obracaniu dlatego spadal do zera bo chcial obrocic i przy jednym sygnale juz wypadal poza max angle!!!! przy nagrywaniu dema to odkrylem
dodatkowo wylaczylem max kat bo za szybko sie wylaczalo! usuniecie minusowego reward bo jak zrobilem demo to reward bylo na minusie,
zmniejszylem predkosc obiektow zeby nigdy nie mogly wyjsc poza kamere, dodanie stopni szybkosci kamety, uwaga obiekt w tym srodowisku nie powinien wychodzic poza kamere ale czasem sie to zdarza! max angle na 90 stopni! uczenie 11,

uczenie 11 doprowadzilo do tego ze agent po prostu sie nie ruszal bo dostawal nagrode za stanie w miejscu na poczatku, wiec teraz usunalem to poczatkowe czekanie zmienilem visual observation na nature cnn - bardziej skomplikowane cnn i wieksze demo uczenie 12 i dodatkowo zrobilem wazniejsze gail niz couriosity,

uczenie 12 wgl nie robi progresu - w sumie ok bo to znaczy ze moje srodowisko jest dobrze stworzone, uczenie 13 zwiekszylem hidden unitys z 128 do 512 i num layers z 1 do 3, lacznie z nature cnn siec jest o wiele bardziej skomplikowana

nadal nic sie nie nauczylo, zawiekszam memory size w recurrent zeby pamietalo wiecej danych z 256 na 4096, podwajam wielkosc sieci num layers z 3 na 6 - uczenie 14, zawieszone, robie eksport na chumure 