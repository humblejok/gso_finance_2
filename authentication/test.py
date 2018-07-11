tlist = [0, 1, 2, 3]
tfack = [{"e":96, "f":95}, {"g":94, "h":93}]
tarray = {"z":0, "y":1, "x":{"a":99, "b":98, "c":97, "d":tfack}, "w":tlist}

def child(var):    
    if type(var) is list:
        for i in range(0,len(var)):
            child(var[i])
    elif type(var) is dict :
        for key, value in enumerate(var):
            child(var[value])
    else:
        print(var)

#child(tlist)
#child(tfack)
child(tarray)
