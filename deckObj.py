from random import shuffle

class DeckKittens():
    """An object that allows manipulation of a deck of cards"""
    cards = []

    def __init__(self):
        self.cards = []

    def __len__(self):
        return len(self.cards)

    def draw(self):
        if (len(self.cards) > 0):
            return self.cards.pop(0)
        return "Null card"
    def drawbottom(self):
        if (len(self.cards) > 0):
            return self.cards.pop()
        return "Null card"
    def pushtop(self, card):
        self.cards.insert(0, card)
    def pushbottom(self, card):
        self.cards.append(card)

    # insert 0 -> top
    # insert 1 -> 1 card above
    # insert -1 -> bottom
    # insert -2 -> one card from bottem
    def insert(self, n, card):
        if (n > len(self.cards)):
            self.cards.append(card)
        elif (n < -len(self.cards)):
            self.cards.insert(0, card)
        elif (n == -1):
            self.cards.append(card)
        elif (n < 0):
            self.cards.insert(n+1, card)
        else:
            self.cards.insert(n, card)

    def shuffle(self):
        shuffle(self.cards)

    def peek(self, n=-1):
        if (n == -1):
            return self.cards[0]
        if (n < 0):
            return []
        if (n < len(self.cards)):
            return self.cards[:n]
        return self.cards

    def output(self):
        print(", ".join(self.cards))

    def swap(self, i1, i2):
        try:
            #if (0 <= i1 < len(self.cards) and 0 <= i2 < len(self.cards) and i1 != i2):
            q = self.cards[i1]
            self.cards[i1] = self.cards[i2]
            self.cards[i2] = q
        except:
            print("Invalid swap")

    def reorder(self, orde):
        for i in range(len(orde)):
            if i not in orde:
                print("invalid ord", i, orde)
                return
        li = self.cards[:len(orde)]

        for i in range(len(orde)):
            self.cards[i] = li[orde[i]]



if __name__ == '__main__':
    print("init:")
    deck = DeckKittens()
    deck.pushbottom("a")
    deck.pushbottom("b")
    deck.pushbottom("c")

    deck.output()
    deck.reorder([1,2,0])
    deck.output()