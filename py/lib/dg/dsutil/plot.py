import matplotlib.pyplot as plt

class SeriesAccumulator:
    def __init__(self, maxsz=100):
        self.acc = {}
        self.maxsz = maxsz

    def add(self, series, val):
        if series in self.acc:
            arr = self.acc[series]
        else:
            self.acc[series] = []
            arr = self.acc[series]
        if len(arr) >= self.maxsz:
            arr = arr[1:].append(val)
        else:
            arr.append(val)

class PieChart:
    def __init__(self, vals, labels=None):
        self.vals = vals
        self.labels = labels

    def draw(self):
        if self.labels == None:
            plt.pie(self.vals)
        else:
            plt.pie(self.vals, labels=self.labels)


class LineChart:
    def __init__(self, xlabel='x', ylabel='y', acc=None):
        self.fig, self.ax = plt.subplots(1, 1) 
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.x_start = 0
        self.x_inc = 1

        if acc == None:
            self.acc = SeriesAccumulator()
        else:
            self.acc = acc

    def draw(self):
        xaxis = None
        legend = []
        for series in self.acc.acc:
            vals = self.acc.acc[series]
            if xaxis == None:
                xaxis = [self.x_start + i * self.x_inc for i in range(len(vals))]
            self.ax.plot(xaxis, vals)
            legend.append(series)
        self.ax.legend(legend)
        self.fig.canvas.draw()

