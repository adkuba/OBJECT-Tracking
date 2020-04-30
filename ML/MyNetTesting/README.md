# Opis
Pliki w tym folderze sluzyly do testow mojej sieci ktora opisalem w artykule. Finalna wersja jest w branchu master. Nie zawarlem tu wszystkich plikow tylko czesc.

## Testy
Trenowalem w google cloud. Robilem z tutoriala. Mialem folder ktory caly wysylalem do google cloud i tam sie to uruchamialo i uczylo. Ponizej wyniki, plik 7.py zawiera strukture sieci keras7. <br>

Wyniki sieci testowych
* keras1 - ERR
* keras2 - ERR
* keras3 - ERR
* keras4 - ERR
* keras5 - 63% - 3_1000_800_600
* keras6 - ERR
* keras7 - 77% - 2_960_640
* keras8 - 77% - 0 (NO FILE)
* keras9 - ERR
* keras10 - 84% - 1_640
* keras11 - 81% - 1_1280_combined
* keras12 - 55% - 1_640_nW (no weights from imagenet)
* keras13 - 78% - NONE_MYPOOLING (0 moje global avg pooling)
* keras14 - 66% - X_NONE_MYPOOLING (Xception 0, my global avg pooling)
* keras15 - 79% - 640_BEETWEEN (640 pomiedzy wyjscie z mobilenet a avg pooling)
* keras16 - 55% - 640_FLATTEN (wyjscie z mobilenet flatten - zamiast avg pooling)

Plik commands.sh zawiera komende ktora wysylalem siec do uczenia w google cloud. Figure_1.png i Figure_2.png obrazuja wyniki. datareader.py tworzy te wykresy, finetuning.py dalsze dopracowanie sieci - powoli ucze warstwy cnn. podobne_obrazki.md zawieraja opis jak tworzylem siec.

## Analiza
Folder analiza pokazuje jak obiekt sie porusza plus pare innych wartosci. Ciekawie to wyglada plus pamietam ze do czegos to sie nawet przydalo.