SBOX = bytearray(b'c|w{\xf2ko\xc50\x01g+\xfe\xd7\xabv\xca\x82\xc9}\xfaYG\xf0\xad\xd4\xa2\xaf\x9c\xa4r\xc0\xb7\xfd\x93&6?\xf7\xcc4\xa5\xe5\xf1q\xd81\x15\x04\xc7#\xc3\x18\x96\x05\x9a\x07\x12\x80\xe2\xeb\'\xb2u\t\x83,\x1a\x1bnZ\xa0R;\xd6\xb3)\xe3/\x84S\xd1\x00\xed \xfc\xb1[j\xcb\xbe9JLX\xcf\xd0\xef\xaa\xfbCM3\x85E\xf9\x02\x7fP<\x9f\xa8Q\xa3@\x8f\x92\x9d8\xf5\xbc\xb6\xda!\x10\xff\xf3\xd2\xcd\x0c\x13\xec_\x97D\x17\xc4\xa7~=d]\x19s`\x81O\xdc"*\x90\x88F\xee\xb8\x14\xde^\x0b\xdb\xe02:\nI\x06$\\\xc2\xd3\xacb\x91\x95\xe4y\xe7\xc87m\x8d\xd5N\xa9lV\xf4\xeaez\xae\x08\xbax%.\x1c\xa6\xb4\xc6\xe8\xddt\x1fK\xbd\x8b\x8ap>\xb5fH\x03\xf6\x0ea5W\xb9\x86\xc1\x1d\x9e\xe1\xf8\x98\x11i\xd9\x8e\x94\x9b\x1e\x87\xe9\xceU(\xdf\x8c\xa1\x89\r\xbf\xe6BhA\x99-\x0f\xb0T\xbb\x16')
REVERSE_SBOX = bytearray(256)
STATE_TEMPLATE = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
def generate_round_constants(len_needed):
    results = bytearray()
    result = 0
    for i in range(1,len_needed+1):
        if i == 1:
            result = 1
        elif result < 0x80:
            result *= 2
        elif result >= 0x80:
            result = (result * 2) ^ 0x11b
        results += bytearray([result,0,0,0])
    return results
def xor(a,b):
    result = []
    for i in range(min(len(a),len(b))):
        result.append(a[i] ^ b[i])
    print("xor:",result,a,b)
    return result
def shift_bytes(inp,shift):
    len_needed = 2 + (shift//len(inp))
    print("shift result:",(inp*len_needed)[shift:][0:4],inp)
    return (inp*len_needed)[shift:][0:4]
def sbox(inp):
    results = []
    for byte in inp:
        results.append(SBOX[byte])
    print("sbox:",results,inp)
    return results
def generate_reverse_sbox():
    global REVERSE_SBOX
    REVERSE_SBOX = bytearray(256)
    for byte in range(0,0x100):
        REVERSE_SBOX[sbox(bytes([byte]))[0]] = byte
def reverse_sbox(inp):
    results = []
    for byte in inp:
        results.append(REVERSE_SBOX[byte])
    print("reverse sbox:",inp,results)
    return results
def to_words(inp):
    result = []
    temp = []
    for byte in inp:
        temp.append(byte)
        if len(temp) >= 4:
            result.append(temp)
            temp = []
    return result
def expand_key(key,size,count):
    if size % 32 != 0 or len(key) != size//8:
        raise ValueError("size must be devideable by 32 and key has to be of the same size")
    result = []
    size = size//32
    consts = to_words(generate_round_constants(count))
    key = to_words(key)
    print(key)
    for i in range(count*size):
        if i < size:
            result.append(key[i:i+1][0])
        elif i % size == 0:
            result.append(xor(xor(consts[(i//size)-1],sbox(shift_bytes(result[i-1],1))),result[i-size]))
        elif size > 6 and i % size == 4:
            result.append(xor(result[i-size],sbox(result[i-1])))
        else:
            result.append(xor(result[i-size],result[i-1]))
        
    return result
def gmul(a,b):
    p = 0
    ao = a
    bo = b
    for i in range(0,8):
        if (bo & 1) != 0:
            p ^= a
        high_bit_set = (ao & 0x80)
        ao <<= 1
        if high_bit_set:
            ao ^= 0x1B
        bo >>= 1
    print("GF multiply", p & 255, a, b)
    return p & 255
def mix_col(inp):
    result = []
    result.append(gmul(inp[0],2) ^ inp[3] ^ inp[2] ^ gmul(inp[1],3))
    result.append(gmul(inp[1],2) ^ inp[0] ^ inp[3] ^ gmul(inp[1],3))
    result.append(gmul(inp[2],2) ^ inp[1] ^ inp[0] ^ gmul(inp[1],3))
    result.append(gmul(inp[3],2) ^ inp[2] ^ inp[1] ^ gmul(inp[1],3))
    print("mix col:",result,inp)
    return result
def mix_cols(inp):
    results = [[],[],[],[]]
    temp = [[],[],[],[]]
    temp2 = []
    for row in inp:
        for i in range(4):
            temp[i].append(row[i])
    for col in temp:
        temp2.append(mix_col(col))
    for row in temp2:
        for i in range(4):
            results[i].append(row[i])
    return results
def shift_rows(inp):
    results = []
    
def setup_state(plaintext,key,size,rounds=-1):
    if size != 128:
        raise ValueError("key must be 128 bit")
    if rounds == -1:
        rounds = 11
    roundkeys = expand_key(key,size,rounds)
    words = to_words(plaintext)
    print(roundkeys)
    state = words
    print(state)
    return state,roundkeys
def add_round_key(state,key):
    result = STATE_TEMPLATE
    for i in range(4):
        for j in range(4):
            result[i][j] = key[i*4+j] ^ state[i][j]
    print("add round key:",result,state,key)
    return result


