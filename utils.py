from psychopy import core, visual, gui, monitors, event
from datetime import date
import pandas as pd
import json
import glob
import os
import numpy as np
import sys

def SignFunc(frameInfo, clock):
    frameInfo["timestamps"].append(clock.getTime())
    return

def get_stimulation_params(path):
    with open(path) as g:
        params_stim = json.loads(g.read())
    params_stim["ori_grating"] = (180*np.arange(params_stim["Nori_grating"])/params_stim["Nori_grating"]).tolist()
    params_stim["Nf_stim"] = int(params_stim["stim_duration"] /(1/60))
    params_stim["Nf_blank"]= int(params_stim["blank_duration"]/(1/60))
    return params_stim

def load_last_mon():
    with open('./Monitors/last_mon.json') as f:
        monInfo = json.loads(f.read())
    return monInfo

def setup_exp():
    monInfo = load_last_mon()
    myDlg = gui.Dlg(title="Stimulation experiment")
    myDlg.addField('Animal species', choices=['mouse', 'rat', 'cat'])
    myDlg.addField('id:', 'mouse01')
    myDlg.addField('date', date.today().strftime("%d-%m-%Y"))
    myDlg.addField('section', choices=list(np.arange(10) + 1))
    myDlg.addField('monitor', monInfo['name'])
    myDlg.addField('distance', monInfo['distance'])
    expInfo = myDlg.show()  # show dialog and wait for OK or Cancel
    if myDlg.OK:  # or if ok_data is not None
        pass
    else:
        core.quit()
    monInfo['name'] = expInfo[4]
    monInfo['distance'] = expInfo[5]

    #check whether monitor information is already inserted
    mon_path = os.path.join('./Monitors', monInfo['name']+ '.json')
    if not os.path.isfile(mon_path):
        monDlg = gui.Dlg(title= "insert Monitor details")
        monDlg.addField('name', choices=[monInfo['name']])
        monDlg.addField('width in cm',)
        monDlg.addField('width in pixels',)
        monDlg.addField('height in pixels',)
        monDlg.addField('distance', monInfo['distance'])
        mon_details= monDlg.show()  # show dialog and wait for OK or Cancel
        if monDlg.OK:  # or if ok_data is not None
            monInfo = {'name': mon_details[0],
                       'width': mon_details[1],
                       'pixels': [int(mon_details[2]), int(mon_details[3])],
                       'distance': mon_details[4]
           }
        else:
            core.quit()
    data2jsonfile(mon_path, monInfo)
    data2jsonfile('./Monitors/last_mon.json', monInfo)
    with open(mon_path) as f:
        monInfo = json.loads(f.read())
    return expInfo, monInfo

def setup_mon(monInfo):
    mon = monitors.Monitor(monInfo['name'])
    mon.setDistance(monInfo['distance'])
    mon.setWidth(monInfo['width'])
    mon.setSizePix(monInfo['pixels'])
    mon.save()
    return mon

def get_mon_info(mon):
    monInfo = {'name': mon.name,
               'width': mon.getWidth(),
               'pixels': mon.getSizePix(),
               'distance': mon.getDistance()
               }
    return monInfo

def create_stimuli(win, part_of_exp, params_stim):
    Nrepeated = params_stim['Nrepeated']
    Nunique = params_stim['Nunique']
    ori_grating = params_stim['ori_grating']
    sf_grating = params_stim['sf_grating']
    size = params_stim['size_of_stimuli']
    path = params_stim['images_path']

    # create images stimuli
    images_r = glob.glob(path + '/*.tif')[0:Nrepeated]
    stim_r = [visual.ImageStim(win, image=i, units='deg', size=size) for i in images_r]
    rep_r = [1 for i in images_r]
    images_u = glob.glob(path + '/*.tif')[Nrepeated + (part_of_exp-1)*Nunique:Nrepeated + part_of_exp*Nunique]
    stim_u = [visual.ImageStim(win, image=i, units='deg', size=size) for i in images_u]
    rep_u = [0 for i in images_u]

    # create grating stimuli
    stim_g = [visual.GratingStim(win, units='deg', sf=sf, ori=ori, size=size) for sf in sf_grating for ori in ori_grating]
    g_id = [[sf,ori] for sf in sf_grating for ori in ori_grating]
    rep_g = [1 for i in g_id]

    #create stim dataframe and shuffle it
    stimuli_dict = { "stimuli" : stim_r + stim_u + stim_g,
                    "stim_id": images_r +images_u + g_id,
                    "rep" : rep_r + rep_u + rep_g
    }
    stim_df = pd.DataFrame(stimuli_dict)
    stim_df = stim_df.sample(frac=1, random_state=1)
    return stim_df

def display_stimuli(data_path, win, stim_df, params_stim, MySignFunc):
        #dictionary of data to store
        frameInfo = {'timestamps': [],
                     'stim_id': [],
                     'rep': []
                     }

        #setup clock
        clock = core.Clock()
        clock.reset()
        for _, row in stim_df.iterrows():
            stimulus = row['stimuli']
            for frame in range(params_stim['Nf_stim']):
                stimulus.draw()
                win.callOnFlip(MySignFunc, frameInfo, clock)
                win.flip()
                if isinstance(stimulus, visual.GratingStim):
                    row['stim_id'] = [stimulus.sf[0], stimulus.ori, stimulus.phase[0]]
                    stimulus.phase += 1 / params_stim['Nf_stim']
                frameInfo['rep'].append(row['rep'])
                frameInfo['stim_id'].append(row['stim_id'])
                if len(event.getKeys()) > 0:
                    sys.exit()
            for frame in range(params_stim['Nf_blank']):
                win.callOnFlip(MySignFunc, frameInfo, clock)
                win.flip()
                frameInfo['stim_id'].append('blank')
                frameInfo['rep'].append(0)
                if len(event.getKeys()) > 0:
                    sys.exit()
        print('duration of section', clock.getTime())
        data2jsonfile(os.path.join(data_path + "/frameInfo.json"), frameInfo)
        return

def save_stim_data(data_path, param_stim, monInfo, stim_df):
    stim_dict = stim_df.filter(('stim_id', 'rep')).to_dict('list')
    data2jsonfile(os.path.join(data_path + "/stimuli_in_order.json"), stim_dict)
    data2jsonfile(os.path.join(data_path + "/monInfo.json"), monInfo)
    data2jsonfile(os.path.join(data_path + "/param_stim.json"), param_stim)
    return

def data2jsonfile(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
    return


# def MySignFunc(timestamps, clock):
#     timestamps.append(clock.getTime())
#     return

# def display_stimuli(data_path, win, stimuli, params_stim):
#     clock = core.Clock()
#     clock.reset()
#     timestamps = []
#     for stimulus in stimuli:
#         for frame in range(params_stim['Nf_stim']):
#             stimulus.draw()
#             win.callOnFlip(MySignFunc, timestamps, clock)
#             win.flip()
#             if isinstance(stimulus, visual.GratingStim):
#                 stimulus.phase += (1 / params_stim['Nf_stim'])
#             if len(event.getKeys()) > 0:
#                 core.quit()
#         for frame in range(params_stim['Nf_blank']):
#             win.callOnFlip(MySignFunc, timestamps, clock)
#             win.flip()
#             if len(event.getKeys()) > 0:
#                 core.quit()
#     data2jsonfile(os.path.join(data_path + "/timestamps.json"),timestamps)
#     return
