

class Distribution:
    def __init__(self, title=''):
        self.dict = {}  # Store item and its frequency pair
        self.title = ''
        if title:
            self.title = f"[== {str(title)} ==]\n"
        
        
    def add(self, item: str):
        item_str = str(item)
        if item_str not in self.dict:
            self.dict[item_str] = 1
        else:
            self.dict[item_str] += 1

    def size(self):
        # The sum of frequency
        size = 0
        for entry in self.dict.items():
            size += entry[1]
        return size
        
    def __str__(self) -> str:
        self.dict = dict(sorted(self.dict.items(), key=lambda x:x[1], reverse=True))
        
        return self.title + str(self.dict)