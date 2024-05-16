from warnings import warn

G = "1011"
FR_SEP = "01111110"


def crc_divrem(x):
    """Zwraca reszte z dzielenia x przez G"""
    n = len(x)
    # liczba bitow do rozepchania z prawej
    pad = "0" * (len(G) - 1)
    # rozepchanie
    xpad = list(x + pad)

    # dopoki jest co odejmowac
    while "1" in xpad[:n]:
        # znajdz pierwsza jedynke po lewej i przesun tam G
        shift = xpad.index("1")
        for i in range(len(G)):
            # xor'uj G z bitami x
            xpad[shift + i] = str(int(G[i] != xpad[shift + i]))

    return "".join(xpad)[n:]


def crc_encode(dword) -> str:
    return dword + crc_divrem(dword)


def crc_decode(dword: str) -> str:
    r = len(G) - 1
    if crc_divrem(dword) == "0" * r:
        return dword[0:-r]
    else:
        warn("\nMALFORMED PACKET\n")
        return ""


def frame_wrap(bits: str, word_size=8) -> str:
    """Koduje odczytane bity kodem crc po 8 bitow, pakuje w ramki"""
    # policz jedynek w FR_SEP
    # jesli w word jest tyle jedynek pod rzad, wloz miedzy nie 0
    words = [
        crc_encode(bits[i : i + word_size]) for i in range(0, len(bits), word_size)
    ]
    cap = FR_SEP.count("1")
    res = []
    for word in words:
        cnt = 0
        for i in range(len(word)):
            if word[i] == "1":
                cnt += 1
                if cnt == cap:
                    print("BEFORE INSERT0", word)
                    word = word[:i] + "0" + word[i:]
                    print("INSERT0 @i={} seq={}".format(i, word))
            else:
                cnt = 0
        res.append(word)
    res = [FR_SEP + word + FR_SEP for word in res]
    return "".join(res)


def frame_unwrap(bits: str) -> str:
    """Odpakowuje bity z ramek i sprawdza kod crc, jesli poprawny usuwa go"""
    words = list(filter(None, bits.split(FR_SEP)))
    # jesli pod rzad mamy ten pattern "11111 0 1"
    # znaczy to (z pewnym prawdopodobienstwem) to 0 zostalo dorzucone przez frame_wrap
    # jezeli w danych (czesci nie-crc) wystapil w "naturalny" sposob taki ciag po ramkowaniu,
    # odramkowanie sie psuje
    cap = FR_SEP.count("1")
    res = []
    for word in words:
        res_word = ""
        cnt = 0
        i = 0
        while i < len(word):
            res_word += word[i]
            if word[i] == "1":
                cnt += 1
                if (
                    cnt == cap - 1
                    and i + 2 < len(word) - (len(G) - 1)
                    and word[i + 2] == "1"
                ):
                    print("SKIP0 @i={} word={}".format(i, word))
                    cnt = 0
                    i += 1
            else:
                cnt = 0
            i += 1
        res.append(res_word)
    words = [crc_decode(res_word) for res_word in res]
    return "".join(words)


def main():
    zfile = open("Z.txt", "r")
    bits = zfile.read().replace("\n", "")
    zfile.close()
    print("BITS TO ENCODE: ", bits)

    coded = frame_wrap(bits)
    print("CRC-ENCODED: ", coded)

    decoded = frame_unwrap(coded)
    print("DECODED: ", decoded)

    if bits == decoded:
        print("SUCCESS")
    else:
        warn("BAD ENCODING")

    wfile = open("W.txt", "w")
    wfile.write(decoded)

    wfile.close()


if __name__ == "__main__":
    main()
