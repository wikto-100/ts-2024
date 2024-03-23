Wiktor Stojek, 272383

Ping:

- Służy do sprawdzania dostępności hostów oraz /min/śr/max/ czasy przepływu pakietów (rtt - całkowity czas przepływu w obie strony).
- Używa domyślnie protokołu sieciowego ICMP

- Można w nim ustawiać wiele flag:
         * -c 17 liczba pakietów do wysłania
         * -s 1472 rozmiar poszczególnego pakietu (standardowo 84 bajty)
        * -M do/want/probe/dont opcja fragmentowania pakietów
        * -i interwał między wysyłaniem pakietów (standardowo 1 sek)
 - Przykładowe wywołanie komendy ping w celu sprawdzenia połączenia z routerem lokalnym:
ping -c 4 -4 -i 0.5 192.168.134.67
 Traceroute:
 - Służy do śledzenia ścieżki pakietów od nadawcy do hosta. Działa poprzez sekwencyjne zwiększanie TTL (time to live) i zwracanie poszczególnych IP, gdzie każdy węzeł przez który przejdzie pakiet zmniejsza TTL o 1.
 - Skrypt tr\_ping.sh robi teoretycznie to samo co traceroute -I, aby zaobserwować ilość skoków wystarczy policzyć który pierwszy ping się udał:
./tr\_ping.sh cia.gov 16 32
traceroute -I cia.gov
 - Używa ICMP/UDP/TCP
 - Przydaje się do diagnozowania czasów przesyłu do poszczególnych węzłów w sieci

 Wireshark:
 - Służy do przechwytywania pakietów (cały ruch sieciowy) w czasie rzeczywistym
 - Analiza zawartości pakietów, mierzenie statystyk
tshark -r nagranie\_wireshark.pcapng -V | grep ICMP -C 5
 (lub uruchomienie GUI wiresharka i załadowanie pliku)
 Można zauważyć (na różowo w GUI) wysyłane i odbierane pakiety ICMP echo, które pochodzą z wcześniejszych komend
 Wpływ wielkości pakietu na jego trasę:
ping 192.168.134.67 -s 1500 -c 1 -M do
ping 192.168.134.67 -s 1400 -c 1 -M do
ping 192.168.134.67 -s 1450 -c 1 -M do
ping 192.168.134.67 -s 1475 -c 1 -M do
ping 192.168.134.67 -s 1460 -c 1 -M do
ping 192.168.134.67 -s 1470 -c 1 -M do
ping 192.168.134.67 -s 1472 -c 1 -M do
ping 192.168.134.67 -s 1473 -c 1 -M do
 Wniosek: wyszukiwanie binarne pokazało, że największym możliwym do wysłania niepofragmentowanym pakietem jest pakiet rozmiaru 1472 (+28 - ramka). Wielkość pakietu może mieć wpływ na jego trasę, ponieważ (w teorii) pewien router może mieć mniejsze MTU i nie przepuścić niepofragmentowanego pakietu.

 Wpływ wielkości pakietu na czas propagacji:
ping wikipedia.org -c 5 -s 800
ping wikipedia.org -c 5 -s 16
ping google.pl -c 5 -s 1200
ping google.pl -c 5 -s 16
ping facebook.com -c 5 -s 800
ping facebook.com -c 5 -s 16

 Zmiana wielkości pakietu nie wpłynęła lub wpłynęła minimalnie na czas propagacji pakietów (avg rtt).

 Wpływ włączenia fragmentacji pakietów na czas propagacji:

ping cia.gov -c 5 -s 500 -M dont
ping cia.gov -c 5 -s 500 -M do

./tr\_ping.sh cia.gov 21 500
./tr\_ping.sh cia.gov 21 16
traceroute -I cia.gov
 Wniosek: włączenie/wyłączenie fragmentacji pakietów nie wpłynęło na czas propagacji ani na trasę skoków
 Wynik traceroute: 19 węzłów.

 Te same zagadnienia dla serwera bliskiego geograficznie:
ping gry.pl -c 5 -s 500 -M dont
ping gry.pl -c 5 -s 500 -M do

./tr\_ping.sh gry.pl 10 1400
./tr\_ping.sh gry.pl 10 16
traceroute -I gry.pl

 Wynik traceroute: 12 węzłów

 Rezultaty dla serwera gry.pl były podobne, z mniejszym rtt avg, około 18 ms.


 Najdłuższa ścieżka jaką udało mi się znaleźć (22 skoki), serwer gdzieś na hawajach
traceroute -I -m 120 45.79.83.116


 Sieci wirtualne stanowią logiczne wyodrębnienie pewnej części sieci fizycznej, dlatego można poznać że pakiet przechodzi przez sieć wirtualną jeżeli dostajemy niespodziewane zmiany w ttl, albo odpowiedzi z wielu różnych adresów IP z bliskiej sobie podsieci.
