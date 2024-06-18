def lzw_compress(uncompressed):
    dictionary = {bytes([i]): i for i in range(256)}
    dict_size = 256
    w = bytes()
    compressed_data = []
    max_code_used = 255 

    for c in uncompressed:
        wc = w + bytes([c])
        if wc in dictionary:
            w = wc
        else:
            compressed_data.append(dictionary[w])
            if len(dictionary) < 4096: 
                dictionary[wc] = dict_size
                dict_size += 1
            w = bytes([c])
            max_code_used = max(max_code_used, dict_size - 1)

    if w:
        compressed_data.append(dictionary[w])
    
    return compressed_data, max_code_used

def lzw_decompress(compressed):
    dictionary = {i: bytes([i]) for i in range(256)}
    dict_size = 256
    result = []

    w = bytes([compressed.pop(0)])
    result.append(w)

    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + bytes([w[0]])
        result.append(entry)

        if len(dictionary) < 4096:
            dictionary[dict_size] = w + bytes([entry[0]])
            dict_size += 1

        w = entry
    
    return b''.join(result) 