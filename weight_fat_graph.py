import datetime as dt
from datetime import date, timedelta
import matplotlib.pyplot as plt
from dateutil import relativedelta

from matplotlib import ticker

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import RangeSlider

import getfit


class weight_fat_graph(FigureCanvasQTAgg):

    def __init__(self):

        # style
        plt.rcParams['font.family'] = 'Noto Sans JP'
        plt.style.use('tableau-colorblind10')

        # data
        self.data = getfit.get_data().fillna(method='ffill').fillna(method='bfill')

        # main graph
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=(10, 6))
        super(weight_fat_graph, self).__init__(self.fig)
        plt.subplots_adjust(bottom=0.3, top=0.9)
        self.ax2 = self.ax1.twinx()
        self.ax1.set_axisbelow(True)
        self.ax1.grid(linestyle='dotted', linewidth=1)

        self.ax3 = self.ax1.figure.add_axes(
            self.ax1.get_position(True),
            sharex=self.ax1,
            sharey=self.ax1,
            frameon=False
        )
        self.ax3.xaxis.set_visible(False)
        self.ax3.yaxis.set_visible(False)

        self.ax1_line = 0
        self.ax2_line = 0
        self.ax1_max_line = 0
        self.ax1_min_line = 0
        self.ax1_ave_line = 0
        self.ax1_max_text = 0
        self.ax1_min_text = 0
        self.ax1_ave_text = 0
        self.ln_v = 0
        self.anno = 0
        self.start_day = dt.datetime(2021, 11, 1).toordinal()
        self.end_day = dt.datetime.now().toordinal()
        self.init_day = dt.datetime(2022, 1, 1).toordinal()

        # slider
        self.freq_slider = RangeSlider(
            ax=plt.axes([0.15, 0.1, 0.65, 0.03]),  # x,y,len,height
            label='Display range',
            valmin=self.start_day,
            valmax=self.end_day,
            valinit=(self.init_day, self.end_day),
            valfmt='%0.0f'
        )
        self.freq_slider.on_changed(self.update_slider)

        # hover
        self.fig.canvas.mpl_connect('motion_notify_event', self.hover)

        self.freq_slider.set_val((self.init_day, self.end_day))
        plt.tick_params(labelsize=10)

    def hover(self, event):
        if event.inaxes is not None and type(self.ax3) == type(event.inaxes):
            target_date = date.fromordinal(int(event.xdata)) + relativedelta.relativedelta(years=1969, days=1)

            if target_date <= date.today():
                weight = self.data['weight'][target_date]
                step = self.data['step'][target_date]
                fat = self.data['fat'][target_date]
                disp_text = '{}\n{:.1f}[kg]\n{}[steps]\n{:.1f}[%]'.format(target_date, weight, step, fat)

                if type(self.ln_v) == int:
                    self.ln_v = self.ax1.axvline(event.xdata, color='gray')
                else:
                    self.ln_v.set(xdata=event.xdata, visible=True)

                if type(self.anno) != int:
                    self.anno.set(text=disp_text, position=(target_date, event.ydata), visible=True)
                else:
                    self.anno = self.ax1.annotate(disp_text, xy=(target_date, event.ydata))
        else:
            if type(self.ln_v) != int:
                self.ln_v.set(visible=False)
                self.anno.set(visible=False)
        plt.draw()

    def update_slider(self, val):
        start_date = dt.datetime.fromordinal(int(val[0]))
        end_date = dt.datetime.fromordinal(int(val[1]))
        input_date_range = ('{}'.format(start_date.date()), '{}'.format(end_date.date()))
        self.freq_slider.valtext.set_text(input_date_range)

        self.ax2.clear()
        self.ax2.grid(False)
        self.plot_graph(start_date, end_date)

    def plot_graph(self, start_date, end_date):
        plot_data = self.data[start_date.date(): end_date.date()]

        max_weight = plot_data['weight'].max()
        ave_weight = plot_data['weight'].mean()
        min_weight = plot_data['weight'].min()
        max_walk = plot_data['step'].max()
        center_pos_x = date.fromordinal(
            int((plot_data.index.max().toordinal() + plot_data.index.min().toordinal()) / 2))

        if type(self.ax1_line) == int:
            self.ax1_line, = self.ax1.plot(plot_data['weight'], color='red', label='weight[kg]')
        else:
            self.ax1_line.set_data(plot_data.index.values, plot_data['weight'])
        self.ax1.set_ylim([min_weight - 0.5, max_weight + 0.5])
        self.ax1.set_xlim(xmin=(start_date.date() - timedelta(days=1)), xmax=end_date.date() + timedelta(days=1))
        self.ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter("%dkg"))

        self.ax2_line = self.ax2.bar(plot_data.index.values, plot_data['step'], alpha=0.3, color='green',
                                     label='steps[num]')
        self.ax2.set_ylim([0, max_walk * 1.2])
        self.ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter("%dsteps"))
        handler1, label1 = self.ax1.get_legend_handles_labels()
        handler2, label2 = self.ax2.get_legend_handles_labels()
        self.ax1.legend(handler1 + handler2, label1 + label2, loc=0)
        self.ax1.yaxis.set_major_locator(MultipleLocator(1))

        for tick in self.ax1.get_xticklabels():
            tick.set_rotation(45)

        if type(self.ax1_max_line) == int:
            self.ax1_max_line = self.ax1.axhline(max_weight, color='red', linestyle='--')
            self.ax1_max_text = self.ax1.text(
                center_pos_x,
                max_weight,
                'max: ' + '{:.2f}'.format(max_weight) + '[kg]',
                fontsize=10,
                va='center',
                ha='center',
                backgroundcolor='w')
        else:
            self.ax1_max_line.set_ydata(max_weight)
            self.ax1_max_text.set(
                x=center_pos_x,
                y=max_weight,
                text='max: ' + '{:.2f}'.format(max_weight) + '[kg]'
            )
        if type(self.ax1_min_line) == int:
            self.ax1_min_line = self.ax1.axhline(min_weight, color='blue', linestyle='--')
            self.ax1_min_text = self.ax1.text(
                center_pos_x,
                min_weight,
                'min: ' + '{:.2f}'.format(min_weight) + '[kg]',
                fontsize=10,
                va='center',
                ha='center',
                backgroundcolor='w')
        else:
            self.ax1_min_line.set_ydata(min_weight)
            self.ax1_min_text.set(
                x=center_pos_x,
                y=min_weight,
                text='min: ' + '{:.2f}'.format(min_weight) + '[kg]')

        if type(self.ax1_ave_line) == int:
            self.ax1_ave_line = self.ax1.axhline(ave_weight, color='orange', linestyle='--')
            self.ax1_ave_text = self.ax1.text(
                center_pos_x,
                ave_weight,
                'ave: ' + '{:.2f}'.format(ave_weight) + '[kg]',
                fontsize=10,
                va='center',
                ha='center',
                backgroundcolor='w')
        else:
            self.ax1_ave_line.set_ydata(ave_weight)
            self.ax1_ave_text.set(
                x=center_pos_x,
                y=ave_weight,
                text='ave: ' + '{:.2f}'.format(ave_weight) + '[kg]')

    def save_picture(self, file_name):
        plt.savefig('image/fig.png')

    def update_graph_data(self):
        self.data = getfit.get_data().fillna(method='ffill').fillna(method='bfill')

    def main(self):
        plt.savefig('image/fig.png')
        plt.show()
