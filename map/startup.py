import random
import sys
import territory

global players

def draft():
    pass # TODO










if __name__ == '__main__':    
    assigner = list(range(42))
    random.shuffle(assigner)
    c = 0
    for i in assigner:
        territory.owner[c] = i % 2
        c += 1

    draft(territory.owner[0])