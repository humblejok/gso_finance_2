class ObfuscationCipher:

    def __init__(self):
        access = 'jkasdASDRAWGch37asdf5d5f4sdf'
        init_key = access[len(access)-1] + access[len(access)-2]
        self.key = [[0]*8,[0]*8]
        for i in range(0,8):
            self.key[0][i] = int('{0:08b}'.format(ord(init_key[0]))[i])
            self.key[1][i] = int('{0:08b}'.format(ord(init_key[1]))[i])

    def cipher_controller(self, data):
        data=str(data)
        self.byte_data = [0]*len(data)
        result = [0]*len(self.byte_data)
        for i in range (0, len(self.byte_data)):
            self.byte_data[i] = '{0:08b}'.format(ord(data[i]))
        i = 0
        if len(data)%2 != 0:
            odd_len_mod=len(self.byte_data)-1
            result[odd_len_mod]=self.byte_data[odd_len_mod]
        else:
            odd_len_mod=len(self.byte_data)
        while i < odd_len_mod:
            data = [0]*2
            data[0] = self.byte_data[i]
            data[1] = self.byte_data[i+1]
            block = self.cipher_core(data, self.key)
            result[i] = block[0]
            result[i+1] = block[1]
            i+=2
        print(result)
        return result

    def cipher_core(self, _data, _key):
        keybuff = _key
        block=[0]*2
        l_part = _data[0]
        r_part = _data[1]
        for j in range(0,16):
            index=j%2
            buff = [0]*8
            for i in range (0,8):
                buff[i] = int(keybuff[index][i]) ^ int(r_part[i])
            keybuff[index] = self.rotate_key(keybuff[index])
            r_part = l_part
            l_part = buff
            block[0] = l_part
            block[1] = r_part
        return block

    def rotate_key(self, r_key):
        buffer = [0]*8
        buffer[0] = int(r_key[7])
        for i in range (0,7):
            buffer[i+1] = int(r_key[i])
        return buffer

    def bintoasc(self, block):
        output = ''
        for i in range(0, len(block)):
            newchar = ''
            for j in range (0,8):
                newchar += str(block[i][j])
            output += chr(int(newchar, 2))
        return output