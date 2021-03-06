from psychopy import visual, gui
import pathlib
import utils
import sys

#get experiment and monitor infos
expInfo, monInfo = utils.setup_exp()

#setup monitor
mon = utils.setup_mon(monInfo)

#get stimulation parameter from file
stim_params_path ='./params_stim.txt'
params_stim = utils.get_stimulation_params(stim_params_path)

#start experiment
section = int(expInfo[3])
while section <= 10:

    # setup window
    win = visual.Window(size=mon.getSizePix(), fullscr=True, color='grey', monitor=mon, screen=0)
    win.recordFrameIntervals = True
    win.refreshThreshold = 1 / 60 + 0.004

    # create folder to store data
    data_path = "./data/%s/%s/%s/section_%s" % (expInfo[0], expInfo[1], expInfo[2], section)
    pathlib.Path(data_path).mkdir(parents=True, exist_ok=True)

    #create stimuli and save data about stimulation (before displaying stimuli)
    stimuli_df = utils.create_stimuli(win, section, params_stim)
    utils.save_stim_data(data_path, params_stim, monInfo, stimuli_df)

    #display stimuli
    utils.display_stimuli(data_path, win, stimuli_df, params_stim, utils.SignFunc)

    # print duration of section and  number of dropped frames
    print('Number of dropped frames =', win.nDroppedFrames)
    win.close()

    section += 1
    # ask if proceding to next section or stop
    if section != 11:
        sectionDlg= gui.Dlg(title="Stimulation experiment")
        sectionDlg.addField('Continue with section:', section)
        Info = sectionDlg.show()  # show dialog and wait for OK or Cancel
        if sectionDlg.OK:  # or if ok_data is not None
            section = int(Info[0])
        else:
            sys.exit()

# import matplotlib.pyplot as plt
# plt.plot(win.frameIntervals)
# plt.show()

