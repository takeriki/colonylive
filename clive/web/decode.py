#!/usr/bin/python
#

def decode_text(text_setting):
    pairs = []
    for line in text_setting.split("\n"):
        if line.strip() == "":
            continue
        conditions, tmp = line.split(":")
        tmp.strip()
        pairs += [(conditions,int(i)) for i in tmp.split(",")]
    return pairs


if __name__ == "__main__":
    txt_test = """
Hfr=tolC:1,2,3

Hfr=folD:1,2,3
"""
    print txt_test
    decode_text(txt_test)

