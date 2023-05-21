from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.config import Config
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
import kivy.utils as utils
import serial.tools.list_ports
import requests
import json
from kivy.core.window import Window
from kivymd.app import MDApp
import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid") #makes the graph look a little nicer
from operator import itemgetter #we use this in the sorting procecure, below
from datetime import datetime
import pandas as pd
import time
import statistics

sensor_id = "sensor-352656103315837"        #RTR device
#sensor_id = "sensor-352656103316116"       #Mike test device

#Global variables
x_plot1 = []
y_plot1 = []
x_plot_his = []
x_plot_his_cor = []
y_plot_his = []
y_plot_his_cor = []
y_plot1_cor = []
x_plot1_cor = []
l_per_m = []
cur_flow_rate = 0
prev_flow_rate = 0
avg_flow_rate = 0
total_tx = 0
last_tx_time = 0

#Plots
fig1 = plt.figure(1)
ax1 = plt.subplot(111)
canvas1 = fig1.canvas
plt.plot()

fig2 = plt.figure(2)
ax2 = plt.subplot(111)
canvas2 = fig2.canvas
plt.plot()

fig3 = plt.figure(3)
ax3 = plt.subplot(111)
canvas3 = fig3.canvas
plt.plot()

fig4 = plt.figure(4)
ax4 = plt.subplot(111)
canvas4 = fig4.canvas
plt.plot()

count = 0

tof_corrected = -2.75e-09

convert_l_m = 2948273550


class Separator(FloatLayout):
    pass

class Spacer(Label):
    pass

#To create an image button, we need to define a class that inherits from button and image classes
class ImageButton(ButtonBehavior, Image):
    pass
class LabelButton(ButtonBehavior, Label):
    pass


class DashboardScreen(Screen):
    pass

class LoginScreen(Screen):
    pass

class SignupScreen(Screen):
    pass

class HistoricScreen(Screen):
    pass


Config.set('graphics', 'width', '1250')
Config.set('graphics', 'height', '650')
Config.write()

class MainApp(MDApp):
    #Global to functions of this class
    
    #Web API key
    #wak = "AIzaSyDwA3LH9iPEORIbp8k1jpPTIQ0GIgzkcdw"
    wak = "AIzaSyAOa_22blGtYpiVy-Lp3evbyRbs_4JGYP4"
    
    iot_device = None
    
    tem_sensor_val = 0
    press_sensor_val = 0
    could_src1_val = 0
    cloud_src2_val = 0
    
    bat1_val = 0
    bat2_val = 0
    
    valve_ctrl1_val = 0
    valve_ctrl2_val = 0
    valve_ctrl3_val = 0
    valve_ctrl4_val = 0
    valve_ctrl5_val = 0
    
    switch1_val = 1
    switch2_val = 0
    
    vol_dis = 0
    pressure_mean = 0
    
    count_id = "03/15/2023 16:24:18"
    
    local_id = ""
    id_token = ""
    
    SearchDict ={}
    SortedDict ={}
    list = []

    
    def build(self):
        GUI = Builder.load_file("main.kv")
        return GUI


    
    def on_start(self):
        LabelBase.register(name='myraid_pro_reg', fn_regular = 'MYRIADPRO-REGULAR.OTF')
        LabelBase.register(name='d_din_reg', fn_regular = 'd-din.regular.ttf')
        LabelBase.register(name='bistecca', fn_regular = 'Bistecca.ttf')
        LabelBase.register(name='teko-reg', fn_regular = 'Teko-Regular.ttf')
        LabelBase.register(name='barlow-reg', fn_regular = 'BarlowSemiCondensed-Regular.ttf')
        LabelBase.register(name='barlow-bold', fn_regular = 'BarlowSemiCondensed-SemiBold.ttf')
        LabelBase.register(name='roboto-medium', fn_regular = 'Roboto-Medium.ttf')
        LabelBase.register(name='roboto-thin', fn_regular = 'Roboto-Thin.ttf')
        
        graph1 = self.root.ids['dashboard_screen'].ids['graph1']
        graph1.add_widget(canvas1)
        fig1.patch.set_alpha(0.0)
        ax1.patch.set_facecolor('#1b203e')
        ax1.spines['bottom'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1)
        ax1.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
        #ax1.plot(x1, y1, color=(0.0039, 0.4392, 0.984), linewidth=6, marker='o')
        ax1.grid(axis= 'y', color='#5D87A1')
        ax1.grid(axis= 'x', color='#1b203e')
        ax1.set_ylabel('Volume (L/m)', fontsize=20)
        ax1.set_xlabel('Time (s)', fontsize=20)
        ax1.xaxis.label.set_color('#5D87A1')
        ax1.yaxis.label.set_color('#5D87A1')
        canvas1.draw_idle()
        
        
        graph2 = self.root.ids['historic_screen'].ids['graph2']
        graph2.add_widget(canvas2)
        fig2.patch.set_alpha(0.0)
        ax2.patch.set_facecolor('#1b203e')
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1)
        ax2.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
        ax2.grid(axis= 'y', color='#5D87A1')
        ax2.grid(axis= 'x', color='#1b203e')
        ax2.set_ylabel('Volume (L/m)', fontsize=20)
        ax2.set_xlabel('Time (s)', fontsize=20)
        ax2.xaxis.label.set_color('#5D87A1')
        ax2.yaxis.label.set_color('#5D87A1')
        
        annot = ax2.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="yellow", ec="black", lw=2),
                    arrowprops=dict(arrowstyle="-"))
        annot.set_visible(False)
        
        
        canvas2.draw_idle()  
        
        graph3 = self.root.ids['historic_screen'].ids['graph3']
        graph3.add_widget(canvas3)
        fig3.patch.set_alpha(0.0)
        ax3.patch.set_facecolor('#1b203e')
        ax3.spines['bottom'].set_visible(False)
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        ax3.spines['left'].set_visible(False)
        ax3.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1)
        ax3.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
        ax3.grid(axis= 'y', color='#5D87A1')
        ax3.grid(axis= 'x', color='#1b203e')
        ax3.set_ylabel('Volume (L/m)', fontsize=20)
        ax3.set_xlabel('Time (s)', fontsize=20)
        ax3.xaxis.label.set_color('#50C878')
        ax3.yaxis.label.set_color('#50C878')
        canvas3.draw_idle()


        bargraph = self.root.ids['dashboard_screen'].ids['bargraph']
        bargraph.add_widget(canvas4)
        fig4.patch.set_alpha(0.0)
        ax4.patch.set_facecolor('#1b203e')
        ax4.grid(axis= 'y', color='#5D87A1')
        ax4.grid(axis= 'x', color='#5D87A1')
        ax4.spines['bottom'].set_visible(False)
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.spines['left'].set_visible(False)
        ax4.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1)
        ax4.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
        D = [('Current FR',0),('Previous FR',0),('Average FR',0)] #enter data for language & popularity
        Dsort = sorted(D, key=itemgetter(1), reverse=False) #sort the list in order of popularity
        
        lang = [x[0] for x in Dsort] #create a list from the first dimension of data
        use  = [x[1] for x in Dsort] #create a list from the second dimension of data
        

        ax4.barh(lang, use, align='center', alpha=0.7, color='r', label='2023', edgecolor = "#5D87A1") #a horizontal bar chart (use .bar instead of .barh for vertical)
        ax4.legend() #puts the year, on the plot
        
        canvas4.draw_idle()

        self.thread_initializations()
        
        
    def search(self, values, searchFor):
        for k, v in values.items():
                for x, y in v.items():
                    if isinstance(y, str):
                        #if searchFor in y:
                        self.list.append(v)
                        self.SearchDict[v['TimeStamp']] = v
                        pressure = v['Pressure']
                        timestamp = v['TimeStamp']
                        self.SortedDict[v['TimeStamp']] = v['Pressure']
                            
                            
    
        return None



    def spinner_clicked(self, value):
        #self.root.ids['historic_screen'].ids['spinner_id'].text = f'Time frame: {value}'
        if self.root.ids['historic_screen'].ids['spinner_id'].text == "1 Hour":
            
            self.root.ids['historic_screen'].ids['avg_flow_time'].text = "Last Hour"
            self.root.ids['historic_screen'].ids['vol_dis_time'].text = "Last Hour"
            self.root.ids['historic_screen'].ids['cum_vol_time'].text = "Last Hour"
            
            global x_plot_his
            global x_plot_his_cor
            global y_plot_his
            global y_plot_his_cor
            
            
            ax2.clear()
            
            #Get the data from the database
            result = requests.get("https://rtr-test-mike-default-rtdb.europe-west1.firebasedatabase.app/" + sensor_id + ".json")
            #Decode the data (from bytes)
            data = json.loads(result.content.decode())   
                             
            now = datetime.now()
            _time = int(time.time() + 60 * 60)
            one_hour_time = _time - (60*60)
            
            
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            _date_time = datetime.utcfromtimestamp(_time).strftime("%m/%d/%Y %H:%M:%S")

            match_dict = {key:val for key, val in data.items() if val['ts'] >= one_hour_time}
            
            #last5pairs = {k: data[k] for k in list(match_dict)[:5]}
            
            my_dict = {k:v['tof'] for k,v in match_dict.items()}
            
            ol_mydict = my_dict.items()
            
            if len(ol_mydict) != 0:
                x_plot_his, y_plot_his = zip(*ol_mydict) # unpack a list of pairs into two tuples
                
            x_plot_his = list(map(int, x_plot_his))
            x_plot_his_cor = [datetime.fromtimestamp(x).strftime("%x %X") for x in x_plot_his]
            
            y_plot_his_cor = tuple(y - tof_corrected for y in y_plot_his)
            l_per_m = tuple(y * convert_l_m for y in y_plot_his_cor)
            
            
                
            if len(ol_mydict) != 0:
                week_fr_mean_list = [float(i) for i in l_per_m]
                week_fr_mean = statistics.mean((week_fr_mean_list))
                week_fr_peak = max(week_fr_mean_list)
                week_fr_sum = sum(week_fr_mean_list)

                
                week_fr_mean = round(week_fr_mean, 2)
                week_fr_peak = round(week_fr_peak, 2)
                week_fr_sum = round(week_fr_sum, 2)
                
                 
                self.root.ids['historic_screen'].ids['avg_flow_rate'].text = f"{week_fr_mean}L/m"
                self.root.ids['historic_screen'].ids['peak_flow_rate'].text = f"{week_fr_peak}L/m"
                self.root.ids['historic_screen'].ids['cum_vol_num'].text = f"{week_fr_sum}L"
                
    
                #PLOT
                ax2.patch.set_facecolor('#1b203e')
                ax2.spines['bottom'].set_visible(False)
                ax2.spines['top'].set_visible(False)
                ax2.spines['right'].set_visible(False)
                ax2.spines['left'].set_visible(False)
                #ax2.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1, rotation=10)
                ax2.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
                ax2.xaxis.set_ticklabels([])
    
                line, = ax2.plot(x_plot_his_cor, l_per_m, color=(0.0039, 0.4392, 0.984, 1), linewidth=6, marker='o')
                ax2.fill_between(x_plot_his_cor,l_per_m,color='blue',alpha=0.2)
                ax2.grid(axis= 'y', color='#5D87A1')
                ax2.grid(axis= 'x', color='#1b203e')
                ax2.set_ylabel('Volume (L/m)', fontsize=20, color=(0.30, 0.82, 0.88, 1.00))
                ax2.set_xlabel('Time (s)', fontsize=20, color=(0.30, 0.82, 0.88, 1.00))
                
                annot = ax2.annotate("", xy=(1,1), xytext=(-20,20),textcoords="offset points",
                bbox=dict(boxstyle="round", fc="yellow", ec="black", lw=2),
                arrowprops=dict(arrowstyle="-", facecolor='black'))
                annot.set_visible(False)
        
                x1_string = list(map(str, x_plot_his_cor))
                y1_string = list(map(str, l_per_m))

        
                def update_annot(ind, x_toplot, y_toplot):
                    x,y = line.get_data()
                    annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
                    text = "{}, {}".format(" ".join([x_toplot[n] for n in ind["ind"]]), 
                                           " ".join([y_toplot[n] for n in ind["ind"]]))
                    annot.set_text(text)
                    annot.get_bbox_patch().set_alpha(0.7)
                    
        
                def hover(event):
                    vis = annot.get_visible()
                    if event.inaxes == ax2:
                        cont, ind = line.contains(event)
                        if cont:
                            update_annot(ind, x1_string, y1_string)
                            annot.set_visible(True)
                            canvas2.draw_idle()
                        else:
                            if vis:
                                annot.set_visible(False)
                                canvas2.draw_idle()

                canvas2.mpl_connect("motion_notify_event", hover)
                
                canvas2.draw_idle()
                
                
                
                moving_averages_x = [] 
                moving_averages_y = [] 
                
                window_size = 3
                i = 0
                total = 0
                
                lstDateTime = [pd.Timestamp(dt) for dt in x_plot_his_cor]
                
                
                if len(lstDateTime) >= 3:
                    while i < len(lstDateTime) - window_size + 1: 
                        # Store elements from i to i+window_size 
                        # in list to get the current window 
                        window_time = lstDateTime[i : i + window_size] 
                        window_value = l_per_m[i : i + window_size] 
                    
                        average_delta_1 = (lstDateTime[i+2] - lstDateTime[i+1]) / 2
                        average_delta_2 = (lstDateTime[i+1] - lstDateTime[i]) / 2
                        average_ts = average_delta_1 + average_delta_2
                        average_ts_total = lstDateTime[i] + average_ts
                        
                        window_average = round(sum(window_value) / window_size, 2) 
                        
                        moving_averages_x.append(average_ts_total.to_pydatetime()) 
                        moving_averages_y.append(window_average) 
                        
                        i += 1
                    
                    res = {}
                    for key in moving_averages_x:
                        for value in moving_averages_y:
                            res[key.strftime('%m/%d/%Y %H:%M:%S')] = value
                            moving_averages_y.remove(value)
                            break
                    
                    ol_Plot = sorted(res.items())
                    
                    x_ma, y_ma = zip(*ol_Plot) # unpack a list of pairs into two tuples
                    
                    ax3.clear()
                    
                    ax3.patch.set_facecolor('#1b203e')
                    ax3.spines['bottom'].set_visible(False)
                    ax3.spines['top'].set_visible(False)
                    ax3.spines['right'].set_visible(False)
                    ax3.spines['left'].set_visible(False)
                    ax3.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1, rotation=10)
                    #ax3.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
                    ax3.xaxis.set_ticklabels([])
                    line2, = ax3.plot(x_ma, y_ma, color='#50C878', linewidth=6, marker='o')
                    ax3.fill_between(x_ma,y_ma,color='green',alpha=0.1)
                    ax3.grid(axis= 'y', color='#5D87A1')
                    ax3.grid(axis= 'x', color='#1b203e')
                    ax3.set_ylabel('Volume (L/m)', fontsize=20)
                    ax3.set_xlabel('Time (s)', fontsize=20)
                    ax3.xaxis.label.set_color('#50C878')
                    ax3.yaxis.label.set_color('#50C878')
                    
                    annot2 = ax3.annotate("", xy=(1,1), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="yellow", ec="black", lw=2),
                    arrowprops=dict(arrowstyle="-", facecolor='black'))
                    annot2.set_visible(False)
            
    
                    x1_string2 = list(map(str, x_ma))
                    y1_string2 = list(map(str, y_ma))
    
            
                    def update_annot2(ind2, x_toplot, y_toplot):
                        x,y = line2.get_data()
                        annot2.xy = (x[ind2["ind"][0]], y[ind2["ind"][0]])
                        text = "{}, {}".format(" ".join([x_toplot[n] for n in ind2["ind"]]), 
                                               " ".join([y_toplot[n] for n in ind2["ind"]]))
                        annot2.set_text(text)
                        annot2.get_bbox_patch().set_alpha(0.7)
                        
            
                    def hover2(event):
                        vis = annot2.get_visible()
                        if event.inaxes == ax3:
                            cont, ind2 = line2.contains(event)
                            if cont:
                                update_annot2(ind2, x1_string2, y1_string2)
                                annot2.set_visible(True)
                                canvas3.draw_idle()
                            else:
                                if vis:
                                    annot2.set_visible(False)
                                    canvas3.draw_idle()
    
                    canvas3.mpl_connect("motion_notify_event", hover2)
                    
                    canvas3.draw_idle()
            
            
        if self.root.ids['historic_screen'].ids['spinner_id'].text == "1 Day":
            
            self.root.ids['historic_screen'].ids['avg_flow_time'].text = "Last Day"
            self.root.ids['historic_screen'].ids['vol_dis_time'].text = "Last Day"
            self.root.ids['historic_screen'].ids['cum_vol_time'].text = "Last Day"
                        

            
            
            ax2.clear()
            
            #Get the data from the database
            result = requests.get("https://rtr-test-mike-default-rtdb.europe-west1.firebasedatabase.app/" + sensor_id + ".json")
            #Decode the data (from bytes)
            data = json.loads(result.content.decode())   
                             
            now = datetime.now()
            _time = int(time.time() + 60 * 60)
            one_day_time = _time - (60*1440)
            
            
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            _date_time = datetime.utcfromtimestamp(_time).strftime("%m/%d/%Y %H:%M:%S")

            match_dict = {key:val for key, val in data.items() if val['ts'] >= one_day_time}
            
            #last5pairs = {k: data[k] for k in list(match_dict)[:5]}
            
            my_dict = {k:v['tof'] for k,v in match_dict.items()}
            
            ol_mydict = my_dict.items()
            
            if len(ol_mydict) != 0:
                x_plot_his, y_plot_his = zip(*ol_mydict) # unpack a list of pairs into two tuples
                
            x_plot_his = list(map(int, x_plot_his))
            x_plot_his_cor = [datetime.fromtimestamp(x).strftime("%x %X") for x in x_plot_his]
            
            y_plot_his_cor = tuple(y - tof_corrected for y in y_plot_his)
            l_per_m = tuple(y * convert_l_m for y in y_plot_his_cor)
            
            
                
            if len(ol_mydict) != 0:
                week_fr_mean_list = [float(i) for i in l_per_m]
                week_fr_mean = statistics.mean((week_fr_mean_list))
                week_fr_peak = max(week_fr_mean_list)
                week_fr_sum = sum(week_fr_mean_list)

                
                week_fr_mean = round(week_fr_mean, 2)
                week_fr_peak = round(week_fr_peak, 2)
                week_fr_sum = round(week_fr_sum, 2)
                
                 
                self.root.ids['historic_screen'].ids['avg_flow_rate'].text = f"{week_fr_mean}L/m"
                self.root.ids['historic_screen'].ids['peak_flow_rate'].text = f"{week_fr_peak}L/m"
                self.root.ids['historic_screen'].ids['cum_vol_num'].text = f"{week_fr_sum}L"
                
    
                #PLOT
                ax2.patch.set_facecolor('#1b203e')
                ax2.spines['bottom'].set_visible(False)
                ax2.spines['top'].set_visible(False)
                ax2.spines['right'].set_visible(False)
                ax2.spines['left'].set_visible(False)
                #ax2.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1, rotation=10)
                ax2.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
                ax2.xaxis.set_ticklabels([])
    
                line, = ax2.plot(x_plot_his_cor, l_per_m, color=(0.0039, 0.4392, 0.984, 1), linewidth=2, marker='o')
                ax2.fill_between(x_plot_his_cor,l_per_m,color='blue',alpha=0.2)
                ax2.grid(axis= 'y', color='#5D87A1')
                ax2.grid(axis= 'x', color='#1b203e')
                ax2.set_ylabel('Volume (L/m)', fontsize=20, color=(0.30, 0.82, 0.88, 1.00))
                ax2.set_xlabel('Time (s)', fontsize=20, color=(0.30, 0.82, 0.88, 1.00))
                
                annot = ax2.annotate("", xy=(1,1), xytext=(-20,20),textcoords="offset points",
                bbox=dict(boxstyle="round", fc="yellow", ec="black", lw=2),
                arrowprops=dict(arrowstyle="-", facecolor='black'))
                annot.set_visible(False)
        
                x1_string = list(map(str, x_plot_his_cor))
                y1_string = list(map(str, l_per_m))

        
                def update_annot(ind, x_toplot, y_toplot):
                    x,y = line.get_data()
                    annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
                    text = "{}, {}".format(" ".join([x_toplot[n] for n in ind["ind"]]), 
                                           " ".join([y_toplot[n] for n in ind["ind"]]))
                    annot.set_text(text)
                    annot.get_bbox_patch().set_alpha(0.7)
                    
        
                def hover(event):
                    vis = annot.get_visible()
                    if event.inaxes == ax2:
                        cont, ind = line.contains(event)
                        if cont:
                            update_annot(ind, x1_string, y1_string)
                            annot.set_visible(True)
                            canvas2.draw_idle()
                        else:
                            if vis:
                                annot.set_visible(False)
                                canvas2.draw_idle()

                canvas2.mpl_connect("motion_notify_event", hover)
                
                canvas2.draw_idle()
                
                
                
                moving_averages_x = [] 
                moving_averages_y = [] 
                
                window_size = 3
                i = 0
                total = 0
                
                lstDateTime = [pd.Timestamp(dt) for dt in x_plot_his_cor]
                
                
                if len(lstDateTime) >= 3:
                    while i < len(lstDateTime) - window_size + 1: 
                        # Store elements from i to i+window_size 
                        # in list to get the current window 
                        window_time = lstDateTime[i : i + window_size] 
                        window_value = l_per_m[i : i + window_size] 
                    
                        average_delta_1 = (lstDateTime[i+2] - lstDateTime[i+1]) / 2
                        average_delta_2 = (lstDateTime[i+1] - lstDateTime[i]) / 2
                        average_ts = average_delta_1 + average_delta_2
                        average_ts_total = lstDateTime[i] + average_ts
                        
                        window_average = round(sum(window_value) / window_size, 2) 
                        
                        moving_averages_x.append(average_ts_total.to_pydatetime()) 
                        moving_averages_y.append(window_average) 
                        
                        i += 1
                    
                    res = {}
                    for key in moving_averages_x:
                        for value in moving_averages_y:
                            res[key.strftime('%m/%d/%Y %H:%M:%S')] = value
                            moving_averages_y.remove(value)
                            break
                    
                    ol_Plot = sorted(res.items())
                    
                    x_ma, y_ma = zip(*ol_Plot) # unpack a list of pairs into two tuples
                    
                    ax3.clear()
                    
                    ax3.patch.set_facecolor('#1b203e')
                    ax3.spines['bottom'].set_visible(False)
                    ax3.spines['top'].set_visible(False)
                    ax3.spines['right'].set_visible(False)
                    ax3.spines['left'].set_visible(False)
                    ax3.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1, rotation=10)
                    #ax3.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
                    ax3.xaxis.set_ticklabels([])
                    line2, = ax3.plot(x_ma, y_ma, color='#50C878', linewidth=6, marker='o')
                    ax3.fill_between(x_ma,y_ma,color='green',alpha=0.1)
                    ax3.grid(axis= 'y', color='#5D87A1')
                    ax3.grid(axis= 'x', color='#1b203e')
                    ax3.set_ylabel('Volume (L/m)', fontsize=20)
                    ax3.set_xlabel('Time (s)', fontsize=20)
                    ax3.xaxis.label.set_color('#50C878')
                    ax3.yaxis.label.set_color('#50C878')
                    #plt.xticks(rotation=15)
                    
                    annot2 = ax3.annotate("", xy=(1,1), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="yellow", ec="black", lw=2),
                    arrowprops=dict(arrowstyle="-", facecolor='black'))
                    annot2.set_visible(False)
            
                    #names = np.array(("12","35","64","36","74","24","463","44"))
    
                    x1_string2 = list(map(str, x_ma))
                    y1_string2 = list(map(str, y_ma))
    
            
                    def update_annot2(ind2, x_toplot, y_toplot):
                        x,y = line2.get_data()
                        annot2.xy = (x[ind2["ind"][0]], y[ind2["ind"][0]])
                        text = "{}, {}".format(" ".join([x_toplot[n] for n in ind2["ind"]]), 
                                               " ".join([y_toplot[n] for n in ind2["ind"]]))
                        annot2.set_text(text)
                        annot2.get_bbox_patch().set_alpha(0.7)
                        
            
                    def hover2(event):
                        vis = annot2.get_visible()
                        if event.inaxes == ax3:
                            cont, ind2 = line2.contains(event)
                            if cont:
                                update_annot2(ind2, x1_string2, y1_string2)
                                annot2.set_visible(True)
                                canvas3.draw_idle()
                            else:
                                if vis:
                                    annot2.set_visible(False)
                                    canvas3.draw_idle()
    
                    canvas3.mpl_connect("motion_notify_event", hover2)
                    
                    canvas3.draw_idle()
        
        if self.root.ids['historic_screen'].ids['spinner_id'].text == "1 Week":
            

            self.root.ids['historic_screen'].ids['avg_flow_time'].text = "Last Week"
            self.root.ids['historic_screen'].ids['vol_dis_time'].text = "Last Week"
            self.root.ids['historic_screen'].ids['cum_vol_time'].text = "Last Week"
            
            ax2.clear()
            
            #Get the data from the database
            result = requests.get("https://rtr-test-mike-default-rtdb.europe-west1.firebasedatabase.app/" + sensor_id + ".json")
            #Decode the data (from bytes)
            data = json.loads(result.content.decode())   
                             
            now = datetime.now()
            _time = int(time.time() + 60 * 60)
            one_week_time = _time - (60*10080)
            
            
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            _date_time = datetime.utcfromtimestamp(_time).strftime("%m/%d/%Y %H:%M:%S")

            match_dict = {key:val for key, val in data.items() if val['ts'] >= one_week_time}
            
            #last5pairs = {k: data[k] for k in list(match_dict)[:5]}
            
            my_dict = {k:v['tof'] for k,v in match_dict.items()}
            
            ol_mydict = my_dict.items()
            
            if len(ol_mydict) != 0:
                x_plot_his, y_plot_his = zip(*ol_mydict) # unpack a list of pairs into two tuples
                
            x_plot_his = list(map(int, x_plot_his))
            x_plot_his_cor = [datetime.fromtimestamp(x).strftime("%x %X") for x in x_plot_his]
            
            y_plot_his_cor = tuple(y - tof_corrected for y in y_plot_his)
            l_per_m = tuple(y * convert_l_m for y in y_plot_his_cor)
            
            
                
            if len(ol_mydict) != 0:
                week_fr_mean_list = [float(i) for i in l_per_m]
                week_fr_mean = statistics.mean((week_fr_mean_list))
                week_fr_peak = max(week_fr_mean_list)
                week_fr_sum = sum(week_fr_mean_list)

                
                week_fr_mean = round(week_fr_mean, 2)
                week_fr_peak = round(week_fr_peak, 2)
                week_fr_sum = round(week_fr_sum, 2)

                 
                self.root.ids['historic_screen'].ids['avg_flow_rate'].text = f"{week_fr_mean}L/m"
                self.root.ids['historic_screen'].ids['peak_flow_rate'].text = f"{week_fr_peak}L/m"
                self.root.ids['historic_screen'].ids['cum_vol_num'].text = f"{week_fr_sum}L"
                
    
                #PLOT
                ax2.patch.set_facecolor('#1b203e')
                ax2.spines['bottom'].set_visible(False)
                ax2.spines['top'].set_visible(False)
                ax2.spines['right'].set_visible(False)
                ax2.spines['left'].set_visible(False)
                ax2.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
                ax2.xaxis.set_ticklabels([])
    
                line, = ax2.plot(x_plot_his_cor, l_per_m, color=(0.0039, 0.4392, 0.984, 1), linewidth=2, marker='o')
                ax2.fill_between(x_plot_his_cor,l_per_m,color='blue',alpha=0.2)
                ax2.grid(axis= 'y', color='#5D87A1')
                ax2.grid(axis= 'x', color='#1b203e')
                ax2.set_ylabel('Volume (L/m)', fontsize=20, color=(0.30, 0.82, 0.88, 1.00))
                ax2.set_xlabel('Time (s)', fontsize=20, color=(0.30, 0.82, 0.88, 1.00))
                
                annot = ax2.annotate("", xy=(1,1), xytext=(-20,20),textcoords="offset points",
                bbox=dict(boxstyle="round", fc="yellow", ec="black", lw=2),
                arrowprops=dict(arrowstyle="-", facecolor='black'))
                annot.set_visible(False)
        
                x1_string = list(map(str, x_plot_his_cor))
                y1_string = list(map(str, l_per_m))

        
                def update_annot(ind, x_toplot, y_toplot):
                    x,y = line.get_data()
                    annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
                    text = "{}, {}".format(" ".join([x_toplot[n] for n in ind["ind"]]), 
                                           " ".join([y_toplot[n] for n in ind["ind"]]))
                    annot.set_text(text)
                    annot.get_bbox_patch().set_alpha(0.7)
                    
        
                def hover(event):
                    vis = annot.get_visible()
                    if event.inaxes == ax2:
                        cont, ind = line.contains(event)
                        if cont:
                            update_annot(ind, x1_string, y1_string)
                            annot.set_visible(True)
                            canvas2.draw_idle()
                        else:
                            if vis:
                                annot.set_visible(False)
                                canvas2.draw_idle()

                canvas2.mpl_connect("motion_notify_event", hover)
                
                canvas2.draw_idle()
                
                
                
                moving_averages_x = [] 
                moving_averages_y = [] 
                
                window_size = 3
                i = 0
                total = 0
                
                lstDateTime = [pd.Timestamp(dt) for dt in x_plot_his_cor]
                
                
                if len(lstDateTime) >= 3:
                    while i < len(lstDateTime) - window_size + 1: 
                        # Store elements from i to i+window_size 
                        # in list to get the current window 
                        window_time = lstDateTime[i : i + window_size] 
                        window_value = l_per_m[i : i + window_size] 
                    
                        average_delta_1 = (lstDateTime[i+2] - lstDateTime[i+1]) / 2
                        average_delta_2 = (lstDateTime[i+1] - lstDateTime[i]) / 2
                        average_ts = average_delta_1 + average_delta_2
                        average_ts_total = lstDateTime[i] + average_ts
                        
                        window_average = round(sum(window_value) / window_size, 2) 
                        
                        moving_averages_x.append(average_ts_total.to_pydatetime()) 
                        moving_averages_y.append(window_average) 
                        
                        i += 1
                    
                    res = {}
                    for key in moving_averages_x:
                        for value in moving_averages_y:
                            res[key.strftime('%m/%d/%Y %H:%M:%S')] = value
                            moving_averages_y.remove(value)
                            break
                    
                    ol_Plot = sorted(res.items())
                    
                    x_ma, y_ma = zip(*ol_Plot) # unpack a list of pairs into two tuples
                    
                    ax3.clear()
                    
                    ax3.patch.set_facecolor('#1b203e')
                    ax3.spines['bottom'].set_visible(False)
                    ax3.spines['top'].set_visible(False)
                    ax3.spines['right'].set_visible(False)
                    ax3.spines['left'].set_visible(False)
                    ax3.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1, rotation=10)
                    #ax3.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
                    ax3.xaxis.set_ticklabels([])
                    line2, = ax3.plot(x_ma, y_ma, color='#50C878', linewidth=6, marker='o')
                    ax3.fill_between(x_ma,y_ma,color='green',alpha=0.1)
                    ax3.grid(axis= 'y', color='#5D87A1')
                    ax3.grid(axis= 'x', color='#1b203e')
                    ax3.set_ylabel('Volume (L/m)', fontsize=20)
                    ax3.set_xlabel('Time (s)', fontsize=20)
                    ax3.xaxis.label.set_color('#50C878')
                    ax3.yaxis.label.set_color('#50C878')
                    #plt.xticks(rotation=15)
                    
                    annot2 = ax3.annotate("", xy=(1,1), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="yellow", ec="black", lw=2),
                    arrowprops=dict(arrowstyle="-", facecolor='black'))
                    annot2.set_visible(False)
            
                    #names = np.array(("12","35","64","36","74","24","463","44"))
    
                    x1_string2 = list(map(str, x_ma))
                    y1_string2 = list(map(str, y_ma))
    
            
                    def update_annot2(ind2, x_toplot, y_toplot):
                        x,y = line2.get_data()
                        annot2.xy = (x[ind2["ind"][0]], y[ind2["ind"][0]])
                        text = "{}, {}".format(" ".join([x_toplot[n] for n in ind2["ind"]]), 
                                               " ".join([y_toplot[n] for n in ind2["ind"]]))
                        annot2.set_text(text)
                        annot2.get_bbox_patch().set_alpha(0.7)
                        
            
                    def hover2(event):
                        vis = annot2.get_visible()
                        if event.inaxes == ax3:
                            cont, ind2 = line2.contains(event)
                            if cont:
                                update_annot2(ind2, x1_string2, y1_string2)
                                annot2.set_visible(True)
                                canvas3.draw_idle()
                            else:
                                if vis:
                                    annot2.set_visible(False)
                                    canvas3.draw_idle()
    
                    canvas3.mpl_connect("motion_notify_event", hover2)
                    
                    canvas3.draw_idle()
        
        if self.root.ids['historic_screen'].ids['spinner_id'].text == "1 Month":            
            
            self.root.ids['historic_screen'].ids['avg_flow_time'].text = "Last Month"
            self.root.ids['historic_screen'].ids['vol_dis_time'].text = "Last Month"
            self.root.ids['historic_screen'].ids['cum_vol_time'].text = "Last Month"
            
            ax2.clear()
            
            #Get the data from the database
            result = requests.get("https://rtr-test-mike-default-rtdb.europe-west1.firebasedatabase.app/" + sensor_id + ".json")
            #Decode the data (from bytes)
            data = json.loads(result.content.decode())   
                             
            now = datetime.now()
            _time = int(time.time() + 60 * 60)
            one_month_time = _time - (60*43800)
            
            
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            _date_time = datetime.utcfromtimestamp(_time).strftime("%m/%d/%Y %H:%M:%S")

            match_dict = {key:val for key, val in data.items() if val['ts'] >= one_month_time}
            
            #last5pairs = {k: data[k] for k in list(match_dict)[:5]}
            
            my_dict = {k:v['tof'] for k,v in match_dict.items()}
            
            ol_mydict = my_dict.items()
            
            if len(ol_mydict) != 0:
                x_plot_his, y_plot_his = zip(*ol_mydict) # unpack a list of pairs into two tuples
                
            x_plot_his = list(map(int, x_plot_his))
            x_plot_his_cor = [datetime.fromtimestamp(x).strftime("%x %X") for x in x_plot_his]
            
            y_plot_his_cor = tuple(y - tof_corrected for y in y_plot_his)
            l_per_m = tuple(y * convert_l_m for y in y_plot_his_cor)
            
            
                
            if len(ol_mydict) != 0:
                week_fr_mean_list = [float(i) for i in l_per_m]
                week_fr_mean = statistics.mean((week_fr_mean_list))
                week_fr_peak = max(week_fr_mean_list)
                week_fr_sum = sum(week_fr_mean_list)

                
                week_fr_mean = round(week_fr_mean, 2)
                week_fr_peak = round(week_fr_peak, 2)
                week_fr_sum = round(week_fr_sum, 2)

                 
                self.root.ids['historic_screen'].ids['avg_flow_rate'].text = f"{week_fr_mean}L/m"
                self.root.ids['historic_screen'].ids['peak_flow_rate'].text = f"{week_fr_peak}L/m"
                self.root.ids['historic_screen'].ids['cum_vol_num'].text = f"{week_fr_sum}L"
                
    
                #PLOT
                ax2.patch.set_facecolor('#1b203e')
                ax2.spines['bottom'].set_visible(False)
                ax2.spines['top'].set_visible(False)
                ax2.spines['right'].set_visible(False)
                ax2.spines['left'].set_visible(False)
                ax2.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
                ax2.xaxis.set_ticklabels([])
    
                line, = ax2.plot(x_plot_his_cor, l_per_m, color=(0.0039, 0.4392, 0.984, 1), linewidth=2, marker='o')
                ax2.fill_between(x_plot_his_cor,l_per_m,color='blue',alpha=0.2)
                ax2.grid(axis= 'y', color='#5D87A1')
                ax2.grid(axis= 'x', color='#1b203e')
                ax2.set_ylabel('Volume (L/m)', fontsize=20, color=(0.30, 0.82, 0.88, 1.00))
                ax2.set_xlabel('Time (s)', fontsize=20, color=(0.30, 0.82, 0.88, 1.00))

                
                annot = ax2.annotate("", xy=(1,1), xytext=(-20,20),textcoords="offset points",
                bbox=dict(boxstyle="round", fc="yellow", ec="black", lw=2),
                arrowprops=dict(arrowstyle="-", facecolor='black'))
                annot.set_visible(False)
        
                #names = np.array(("12","35","64","36","74","24","463","44"))

                x1_string = list(map(str, x_plot_his_cor))
                y1_string = list(map(str, l_per_m))

        
                def update_annot(ind, x_toplot, y_toplot):
                    x,y = line.get_data()
                    annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
                    text = "{}, {}".format(" ".join([x_toplot[n] for n in ind["ind"]]), 
                                           " ".join([y_toplot[n] for n in ind["ind"]]))
                    annot.set_text(text)
                    annot.get_bbox_patch().set_alpha(0.7)
                    
        
                def hover(event):
                    vis = annot.get_visible()
                    if event.inaxes == ax2:
                        cont, ind = line.contains(event)
                        if cont:
                            update_annot(ind, x1_string, y1_string)
                            annot.set_visible(True)
                            canvas2.draw_idle()
                        else:
                            if vis:
                                annot.set_visible(False)
                                canvas2.draw_idle()

                canvas2.mpl_connect("motion_notify_event", hover)
                
                canvas2.draw_idle()
                
                
                
                moving_averages_x = [] 
                moving_averages_y = [] 
                
                window_size = 3
                i = 0
                total = 0
                
                lstDateTime = [pd.Timestamp(dt) for dt in x_plot_his_cor]
                
                
                if len(lstDateTime) >= 3:
                    while i < len(lstDateTime) - window_size + 1: 
                        # Store elements from i to i+window_size 
                        # in list to get the current window 
                        window_time = lstDateTime[i : i + window_size] 
                        window_value = l_per_m[i : i + window_size] 
                    
                        average_delta_1 = (lstDateTime[i+2] - lstDateTime[i+1]) / 2
                        average_delta_2 = (lstDateTime[i+1] - lstDateTime[i]) / 2
                        average_ts = average_delta_1 + average_delta_2
                        average_ts_total = lstDateTime[i] + average_ts
                        
                        window_average = round(sum(window_value) / window_size, 2) 
                        
                        moving_averages_x.append(average_ts_total.to_pydatetime()) 
                        moving_averages_y.append(window_average) 
                        
                        i += 1
                    
                    res = {}
                    for key in moving_averages_x:
                        for value in moving_averages_y:
                            res[key.strftime('%m/%d/%Y %H:%M:%S')] = value
                            moving_averages_y.remove(value)
                            break
                    
                    ol_Plot = sorted(res.items())
                    
                    x_ma, y_ma = zip(*ol_Plot) # unpack a list of pairs into two tuples
                    
                    ax3.clear()
                    
                    ax3.patch.set_facecolor('#1b203e')
                    ax3.spines['bottom'].set_visible(False)
                    ax3.spines['top'].set_visible(False)
                    ax3.spines['right'].set_visible(False)
                    ax3.spines['left'].set_visible(False)
                    ax3.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1, rotation=10)
                    ax3.xaxis.set_ticklabels([])
                    line2, = ax3.plot(x_ma, y_ma, color='#50C878', linewidth=6, marker='o')
                    ax3.fill_between(x_ma,y_ma,color='green',alpha=0.1)
                    ax3.grid(axis= 'y', color='#5D87A1')
                    ax3.grid(axis= 'x', color='#1b203e')
                    ax3.set_ylabel('Volume (L/m)', fontsize=20)
                    ax3.set_xlabel('Time (s)', fontsize=20)
                    ax3.xaxis.label.set_color('#50C878')
                    ax3.yaxis.label.set_color('#50C878')
                    
                    annot2 = ax3.annotate("", xy=(1,1), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="yellow", ec="black", lw=2),
                    arrowprops=dict(arrowstyle="-", facecolor='black'))
                    annot2.set_visible(False)
                
                    x1_string2 = list(map(str, x_ma))
                    y1_string2 = list(map(str, y_ma))
    
            
                    def update_annot2(ind2, x_toplot, y_toplot):
                        x,y = line2.get_data()
                        annot2.xy = (x[ind2["ind"][0]], y[ind2["ind"][0]])
                        text = "{}, {}".format(" ".join([x_toplot[n] for n in ind2["ind"]]), 
                                               " ".join([y_toplot[n] for n in ind2["ind"]]))
                        annot2.set_text(text)
                        annot2.get_bbox_patch().set_alpha(0.7)
                        
            
                    def hover2(event):
                        vis = annot2.get_visible()
                        if event.inaxes == ax3:
                            cont, ind2 = line2.contains(event)
                            if cont:
                                update_annot2(ind2, x1_string2, y1_string2)
                                annot2.set_visible(True)
                                canvas3.draw_idle()
                            else:
                                if vis:
                                    annot2.set_visible(False)
                                    canvas3.draw_idle()
    
                    canvas3.mpl_connect("motion_notify_event", hover2)
                    
                    canvas3.draw_idle()
        
        
    def process_signup(self):
        self.sign_up(self.root.ids['signup_screen'].ids['sign_up_email_id'].text, self.root.ids['signup_screen'].ids['sign_up_password_id'].text)
        

    def sign_up(self, email, password):
        #send email and password to firebase
        #Firebase gives back localId, idToken, refreshToken
        #localId = unique identifier for the email and password
        #localId is used this as our new device ID
        
        #The idToken is going to be sent to Firebase so that the user can be authenticated 
        #Authentication expires after an hour
        
        #Refresh token does not expire, we use this to automatically get a new idToken to sign back in
        #So we store the refresh token on the local disk and we read the file to do automatic signin
        
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key="+self.wak
        
        #Signup new user
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        
        print(sign_up_request.ok)
        print(sign_up_request.content.decode())
        sign_up_data = json.loads(sign_up_request.content.decode())
        
        
        if sign_up_request.ok == False:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data["error"]["message"]
            
            self.root.ids['signup_screen'].ids['error_label_id'].text = error_message
            self.root.ids['signup_screen'].ids['error_label_id'].color = utils.get_color_from_hex("#ff0000")
            
        if sign_up_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            self.local_id = sign_up_data['localId']
            self.id_token = sign_up_data['idToken']         #Store this on the disk so it perisists
            print("ID TOKEN", self.id_token)
            
            with open("refresh_token.txt", "w") as f:
                f.write(refresh_token)
           
            #Create new key in database from localId
            #Set default values for this new device
            device_data = '{"Temperature":0, "Pressure":0, "battery1":0, "battery2":0, "cloud1":0, "cloud2":0, "switch1":0, "switch2":0}'
            requests.patch("https://dashboardiot-6efa4-default-rtdb.firebaseio.com/"+self.local_id+".json?auth="+self.id_token, data=device_data)
            
            requests.patch("https://dashboardiot-6efa4-default-rtdb.firebaseio.com/1"+".json?auth="+self.id_token, data=device_data)

            
            self.root.current = 'login_screen'
    def process_login(self):

        login_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key="+self.wak
        
        #Signup new user
        login_payload = {"email": "example@email.ie", "password": "password", "returnSecureToken": True}
        login_request = requests.post(login_url, data=login_payload)
        
        print(login_request.ok)
        print(login_request.content.decode())
        login_data = json.loads(login_request.content.decode())
        
        if login_request.ok == False:
            error_data = json.loads(login_request.content.decode())
            error_message = error_data["error"]["message"]
            print("Login error")
            
        if login_request.ok == True:
            refresh_token = login_data['refreshToken']
            self.local_id = login_data['localId']
            self.id_token = login_data['idToken']         #Store this on the disk so it perisists
            print("LOGIN ID TOKEN", self.id_token)
            
            with open("refresh_token.txt", "w") as f:
                f.write(refresh_token)
        
        self.root.current = 'dashboard_screen'
        
    def process_signup_btn(self):
        self.root.current = 'signup_screen'
        
    def process_login_btn(self):
        self.root.current = 'login_screen'
        
    def close(self):
        quit()
    def minimize(self):
        Window.minimize()
        
    def get_port(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if port.manufacturer.startswith('STM'):
                port_number = port.device
    
        return port_number
    
    def thread_initializations(self):
        #try:
        #    self.iot_device = serial.Serial(port = self.get_port(), baudrate = 115200, 
        #                                    bytesize =serial.EIGHTBITS, 
        #                                    parity = serial.PARITY_NONE, timeout = 1)
        #except:
        #    print("Device not connected")
        Clock.schedule_interval(self.update_dashboard_ui, 1)        #Main thread - Run every second
        
        #self.main_thread = Thread(target = self.get_sensor_data)    #Pass the target thread function
        #self.main_thread.daemon  = True                             #Run without blocking the main program from exiting
                                                                    #If the Thread ins't daomon, it blocks the main thread from exiting
                                                                    #until that thread is killed
        #self.main_thread.start()
            
    def get_sensor_data(self):
        while True:
            try:
                value = self.iot_device.readline()
            except:
                #print("Nothing to print")
                pass
            try:
                new_value = int(value[1:].decode("utf-8"))               #Skip the first character (letter A) and get all subsequent 
                if chr(value[0]) == 'A':
                    self.tem_sensor_val = new_value
                if chr(value[0]) == 'B':
                    self.press_sensor_val = new_value
                if chr(value[0]) == 'C':
                    self.bat1_val = new_value
                if chr(value[0]) == 'D':
                    self.bat2_val = new_value
            except:
                pass
            
    def update_dashboard_ui(self, arg):
        #Run every second
        global count
        global x_plot1
        global y_plot1
        global y_plot1_cor
        global x_plot1_cor
        global cur_flow_rate
        global prev_flow_rate
        global avg_flow_rate
        global l_per_m
        global total_tx
        global last_tx_time
        count += 1
        
        try:
            if (count%10) == 0:
                
                #Get the data from the database
                result = requests.get("https://rtr-test-mike-default-rtdb.europe-west1.firebasedatabase.app/" + sensor_id + ".json")
                #Decode the data (from bytes)
                data = json.loads(result.content.decode())

                total_tx = len(data)

                _time = int(time.time() + 60 * 60)
                _date_time = datetime.utcfromtimestamp(_time).strftime('%H:%M:%S')
                
                last50pairs = {k: data[k] for k in list(data)[-15:]}
                
                mydict = {}
                ol_mydict = []
                mydict = {k:v['tof'] for k,v in last50pairs.items()}

                ol_mydict = mydict.items()
                                
                if len(ol_mydict) != 0:
                    x_plot1, y_plot1 = zip(*ol_mydict) # unpack a list of pairs into two tuples
                    

                x_plot1 = list(map(int, x_plot1))
                x_plot1_cor = [datetime.fromtimestamp(x).strftime("%X") for x in x_plot1]
                last_tx_time = x_plot1_cor[-1]
                y_plot1_cor = tuple(y - tof_corrected for y in y_plot1)
                l_per_m = tuple(y * convert_l_m for y in y_plot1_cor)

                cur_flow_rate = l_per_m[-1]
                cur_flow_rate = str(round(cur_flow_rate, 2))
                prev_flow_rate = l_per_m[-2]
                prev_flow_rate = str(round(prev_flow_rate, 2))
                avg_flow_rate = sum(l_per_m) / len(l_per_m)
                avg_flow_rate = str(round(avg_flow_rate, 2))
        except:
            print("Errorino MDB")
        
        
            

        if count <= 10:
            ax1.clear()
            ax1.patch.set_facecolor('#1b203e')
            ax1.grid(axis= 'y', color='#5D87A1')
            ax1.set_ylabel('Volume (L/m)', fontsize=20)
            ax1.set_xlabel('Time (s)', fontsize=20)

            

        if count >= 10:
            ax1.clear()
            ax1.patch.set_facecolor('#1b203e')
            ax1.grid(axis= 'y', color='#5D87A1')
            ax1.set_ylabel('Volume (L/m)', fontsize=20)
            ax1.set_xlabel('Time', fontsize=20)
            ax1.tick_params(axis='x', labelsize=12, size=0.1)

            
            ax4.clear()
            ax4.patch.set_facecolor('#1b203e')
            ax4.grid(axis= 'y', color='#5D87A1')
            ax4.grid(axis= 'x', color='#5D87A1')
            ax4.tick_params(axis='x', colors='#5D87A1', labelsize=16, size=0.1)
            ax4.tick_params(axis='y', colors='#5D87A1', labelsize=16, size=0.1)
            D = [('Current FR',float(cur_flow_rate)),('Previous FR',float(prev_flow_rate)),('Average FR',float(avg_flow_rate))] #enter data for language & popularity
            Dsort = sorted(D, key=itemgetter(1), reverse=False) #sort the list in order of popularity
            
            lang = [x[0] for x in Dsort] #create a list from the first dimension of data
            use  = [x[1] for x in Dsort] #create a list from the second dimension of data
            
    
            ax4.barh(lang, use, align='center', alpha=0.7, color='r', label='2023', edgecolor = "#5D87A1") #a horizontal bar chart (use .bar instead of .barh for vertical)
            ax4.legend() #puts the year, on the plot
                        
        
        ax1.plot(x_plot1_cor, l_per_m, color=(0.0039, 0.4392, 0.984, 1), linewidth=6, marker='o')
        ax1.fill_between(x_plot1_cor,l_per_m,color='blue',alpha=0.2)
        
        canvas1.draw_idle()
        canvas4.draw_idle()
        
        try:

            self.root.ids['dashboard_screen'].ids['temp_sensor_label_id'].text = str(cur_flow_rate) + " L/m"
            if float(cur_flow_rate) > 120.0:
                self.root.ids['dashboard_screen'].ids['temp_sensor_img_id'].source = "icons/7.png"
            elif float(cur_flow_rate) > 100.0:
                self.root.ids['dashboard_screen'].ids['temp_sensor_img_id'].source = "icons/6.png"
            elif float(cur_flow_rate) > 85.0:
                self.root.ids['dashboard_screen'].ids['temp_sensor_img_id'].source = "icons/5.png"
            elif float(cur_flow_rate) > 55.0:
                self.root.ids['dashboard_screen'].ids['temp_sensor_img_id'].source = "icons/4.png"
            elif float(cur_flow_rate) > 25.0:
                self.root.ids['dashboard_screen'].ids['temp_sensor_img_id'].source = "icons/3.png"     
            elif float(cur_flow_rate) > 5.0:
                self.root.ids['dashboard_screen'].ids['temp_sensor_img_id'].source = "icons/2.png"
            elif float(cur_flow_rate) > 0.0:
                self.root.ids['dashboard_screen'].ids['temp_sensor_img_id'].source = "icons/1.png"  
            else:
                self.root.ids['dashboard_screen'].ids['temp_sensor_img_id'].source = "icons/0.png"
                  
            
            self.root.ids['dashboard_screen'].ids['prev_flow_rate'].text = str(prev_flow_rate)
            self.root.ids['dashboard_screen'].ids['avg_flow_rate'].text = str(avg_flow_rate)
            self.root.ids['dashboard_screen'].ids['transmission_rate'].text = str(total_tx)
            self.root.ids['dashboard_screen'].ids['transmission_rate'].text = str(total_tx)
            
            
            _battery1 = 0                
            _battery2 = 0
            self.root.ids['dashboard_screen'].ids['bat2_img_id'].source = "icons/bat4.png"
            self.root.ids['dashboard_screen'].ids['last_tx_time'].text = "Last TX time: " + str(last_tx_time)
            
        except:
            print("Errorino2")
            
            
            
            
    
    def process_dashboard(self):
        self.root.current = 'dashboard_screen'
    
    def process_historic(self):
        self.root.current = 'historic_screen'
    
    def process_configuration(self):
        self.root.current = 'login_screen'
        
    def process_switch1(self):
        #Check whether siwtch 1 is on or not
        if self.switch1_val:
            self.root.ids['dashboard_screen'].ids['switch_1_id'].source = "icons/switchon.png" 
            self.root.ids['dashboard_screen'].ids['switch_1_label_id'].text = "ON" 
            self.root.ids['dashboard_screen'].ids['switch_1_label_id'].color = utils.get_color_from_hex("#27eea0")
            
            self.switch1_val = 0
            #Switch 1 on - A1, Switch 1 off - A0
            self.send_data('A1')
            print("Switch 1 toggled ON")
        else:
            self.root.ids['dashboard_screen'].ids['switch_1_id'].source = "icons/switchoff.png" 
            self.root.ids['dashboard_screen'].ids['switch_1_label_id'].text = "OFF" 
            self.root.ids['dashboard_screen'].ids['switch_1_label_id'].color = utils.get_color_from_hex("#0b172e")
            
            self.switch1_val = 1
            self.send_data('A0')
            print("Switch 1 toggled OFF")
            
    def process_switch2(self):
        #Check whether siwtch 1 is on or not
        if self.switch2_val:
            self.root.ids['dashboard_screen'].ids['switch_2_id'].source = "icons/switchon.png" 
            self.root.ids['dashboard_screen'].ids['switch_2_label_id'].text = "ON" 
            self.root.ids['dashboard_screen'].ids['switch_2_label_id'].color = utils.get_color_from_hex("#27eea0")
            
            self.switch2_val = 0
            #Switch 2 on - B1, Switch 1 off - B0
            self.send_data('B1')
            print("Switch 2 toggled ON")
        else:
            self.root.ids['dashboard_screen'].ids['switch_2_id'].source = "icons/switchoff.png" 
            self.root.ids['dashboard_screen'].ids['switch_2_label_id'].text = "OFF" 
            self.root.ids['dashboard_screen'].ids['switch_2_label_id'].color = utils.get_color_from_hex("#0b172e")
            
            self.switch2_val = 1
            self.send_data('B0')
            print("Switch 2 toggled OFF")
            
            
    def send_data(self, data):
        try:
            self.iot_device.write(data.encode())
        except:
            print("Nothing to send")
            
MainApp().run()