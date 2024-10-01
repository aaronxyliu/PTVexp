import matplotlib.pyplot as plt
import numpy as np

# Frequency
class Distribution:
    def __init__(self):
        self.dict = {}  # Store item and its frequency pair
        
    def add(self, item: str, value: str = ''):
        item_str = str(item)
        value_str = str(value)
        if item_str not in self.dict:
            self.dict[item_str] = [value_str]
        else:
            self.dict[item_str].append(value_str)

    def size(self):
        # The sum of frequency
        size = 0
        for entry in self.dict.items():
            size += len(entry[1])
        return size
        
    def freqDict(self, title: str = None) -> str:
        # Frequency Distribution
        frequency_dict = {}
        for pair in self.dict.items():
            frequency_dict[pair[0]] = len(pair[1])

        # Sort by frequency from high to low
        frequency_dict = dict(sorted(frequency_dict.items(), key=lambda x:x[1], reverse=True))
        if title:
            return f"[== {str(title)} ==]\n" + str(frequency_dict)
        else:
            return frequency_dict
    
    def avgDateDict(self, title: str = None) -> str:
        # Average Date Distribution
        average_dict = {}
        for entry in self.dict.items():
            average_dict[entry[0]] = self.avgDate(entry[1])
        average_dict = dict(sorted(average_dict.items(), key=lambda d: int(''.join(d[1].split('-'))), reverse=True))
        
        if title:
            return f"[== {str(title)} ==]\n" + str(average_dict)
        else:
            return average_dict
    
    def avgDate(self, dates: list) -> str:
        # Calculate the average date for a list of dates
        if not dates or len(dates) == 0:
            return ''
        mean_date = (np.array(dates, dtype='datetime64[s]')
                            .view('i8')
                            .mean()
                            .astype('datetime64[s]'))
        return str(mean_date)[:10]
    
    def showplot(self, title: str = None, xlabel: str = None, ylabel: str = None):
        freq_dict = self.freqDict()
        # Sort by item name
        freq_dict = dict(sorted(freq_dict.items(), key=lambda x:x[0], reverse=False))

        x_list = []
        y_list = []
        for pair in freq_dict.items():
            x_list.append(pair[0])
            y_list.append(pair[1])

        plt.bar(x=range(len(x_list)), height=y_list, width=0.5,
            color="#F5CCCC",
            edgecolor="#C66667")

        plt.xticks(range(len(x_list)), x_list)
        plt.xlabel(xlabel or "Item")
        plt.ylabel(ylabel or "Frequency")

        plt.rcParams['figure.figsize'] = [6.2, 3]
        if title:
            plt.title(title)
        plt.show()


    

d = Distribution()
d.add('x', '2012-02-13')
d.add('x', '2012-02-15')
d.add('y', '2013-02-15')
d.add('z', '2010-02-15')
print(d.freqDict('Title'))