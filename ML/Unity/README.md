# Setup
Zainstalowalem z oficjalnego repo unity ml-agents [poradnik](https://github.com/Unity-Technologies/ml-agents/blob/latest_release/docs/Readme.md) <br>
Pracuje na osobnym branchu ```git checkout -b UnityML_Testing``` <br>
Trzeba zaimportowac paczke ml-agents w nowym projekcie, przyklady sa w Projects/Assets/Examples z nich bede korzystal <br>
Przydatna komenda w vs code do auto formatowania kodu ```Ctrl + Shift + I```

# Unity environment
Opis srodowiska w unity do machine learning.
## Test version
Unity bedzie sterowalo kamera w osi Y, obserwacja (danymi wejsciowymi do sieci) bedzie obraz z kamery. <br>
Pusty obiekt GameController wybiera losowo przedmiot ktory bedzie sledzonym obiektem. Na podstawie sledzonego bedzie wyliczany wynik - odchylenie od srodka kamery, dazymy do zminimalizowania tej wartosci. Obiekty poruszaja sie losowo po planszy. Moze byc wiecej niz jeden obiekt z prefabu.