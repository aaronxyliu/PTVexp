import matplotlib.pyplot as plt
import numpy as np

# Frequency
class Distribution:
    def __init__(self):
        self.dict = {}  # Store item and its frequency pair
        
    def add(self, item: str, value: str = ''):
        item_str = str(item)
        if item_str not in self.dict:
            self.dict[item_str] = [value]
        else:
            self.dict[item_str].append(value)

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
        # average_dict = dict(sorted(average_dict.items(), key=lambda d: int(''.join(d[1].split('-'))), reverse=True))
        
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
    
    def showplot(self, title: str = None, processFunc = None, xlabel: str = None, ylabel: str = None, sortByY: bool = False, head: int = -1):
        # "processFunc' must be a function that receives a list and returns a number

        if len(self.dict) == 0:
            return

        show_dict = {}
        for pair in self.dict.items():
            if not processFunc:
                # Calculate the frequency by default
                show_dict[pair[0]] = len(pair[1])
            else:
                show_dict[pair[0]] = float(processFunc(pair[1]))

        # Sort by X or Y
        if sortByY:
            show_dict = dict(sorted(show_dict.items(), key=lambda x:x[1], reverse=True))
        else:
            show_dict = dict(sorted(show_dict.items(), key=lambda x:x[0], reverse=False))

        x_list = []
        y_list = []
        
        i = 0
        for pair in show_dict.items():
            if head > 0 and i >= head:
                break
            x_list.append(pair[0])
            y_list.append(pair[1])
            i += 1

        plt.bar(x=range(len(x_list)), height=y_list, width=0.5,
            color="#F5CCCC",
            edgecolor="#C66667")

        plt.xticks(range(len(x_list)), x_list)
        plt.xlabel(xlabel or "Item")
        plt.ylabel(ylabel or "Frequency")

        plt.xticks(rotation=-40)

        plt.rcParams['figure.figsize'] = [6.2, 3]
        if title:
            plt.title(title)
        plt.show()

    def showsbplot(self, title: str = None, processFunc = None, xlabel: str = None, ylabel: str = None, sortByY: bool = False, head: int = -1):
        # stacked bar plot
        # "processFunc' must be a function that receives a list and returns a dict

        item_len = len(self.dict)
        if item_len == 0:
            return
        
        fig, ax = plt.subplots()
        bottom = np.zeros(item_len)
        width = 0.4

        x_list = []
        
        stack_dicts = []
        for pair in self.dict.items():
            x_list.append(pair[0])
            stack_dicts.append(processFunc(pair[1]))

        for k, _ in stack_dicts[0]:
            weights = np.array()
            for stack_dict in stack_dicts:
                weights = np.append(weights, stack_dict[k])
            ax.bar(x_list, weights, width, label=str(k), bottom=bottom) 
            bottom += weights

        
        ax.set_title("Number of penguins with above average body mass")
        ax.legend(loc="upper right")

        plt.show()
                    

            