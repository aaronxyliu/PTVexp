import matplotlib.pyplot as plt
import numpy as np

# Frequency
class Distribution:
    def __init__(self, title=''):
        self.dict = {}  # Store item and its frequency pair
        self.title = title
        
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
        # Sort by frequency
        self.dict = dict(sorted(self.dict.items(), key=lambda x:x[1], reverse=True))
        title = ''
        if self.title:
            title = f"[== {str(self.title)} ==]\n"
        return title + str(self.dict)
    
    def showplot(self):
        # Sort by item name
        self.dict = dict(sorted(self.dict.items(), key=lambda x:x[0], reverse=False))

        x_list = []
        y_list = []
        for pair in self.dict.items():
            x_list.append(pair[0])
            y_list.append(pair[1])

        plt.bar(x=range(len(x_list)), height=y_list, width=0.5,
            color="#F5CCCC",
            edgecolor="#C66667")

        plt.xticks(range(len(x_list)), x_list)
        plt.xlabel("Item")
        plt.ylabel("Frequency")

        plt.rcParams['figure.figsize'] = [6.2, 3]
        plt.title(self.title)
        plt.show()


# Sum
class Distribution2:
    def __init__(self, title=''):
        self.dict = {}  
        self.title = title
        
    def add(self, item: str, value: str):
        item_str = str(item)
        if item_str not in self.dict:
            self.dict[item_str] = [value]
        else:
            self.dict[item_str].append(value)

        
    def __str__(self) -> str:
        self.average_dict = {}
        for entry in self.dict.items():
            self.average_dict[entry[0]] = self.average_date(entry[1])
        self.average_dict = dict(sorted(self.average_dict.items(), key=lambda d: int(''.join(d[1].split('-'))), reverse=True))
        
        title = ''
        if self.title:
            title = f"[== {str(self.title)} ==]\n"
        return title + str(self.average_dict)
    
    def average_date(self, dates: list) -> str:
        if not dates or len(dates) == 0:
            return ''
        mean_date = (np.array(dates, dtype='datetime64[s]')
                            .view('i8')
                            .mean()
                            .astype('datetime64[s]'))
        return str(mean_date)[:10]
    

d = Distribution2()
d.add('x', '2012-02-13')
d.add('x', '2012-02-15')
d.add('y', '2013-02-15')
d.add('z', '2010-02-15')
print(d)