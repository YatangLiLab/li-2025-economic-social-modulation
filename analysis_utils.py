# -*- coding: utf-8 -*-
"""
Authors:
    Zhe Li
    Yatang Li

Created: 2023-06-20
Last updated: 2025-07-11

"""


import os
import sys
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import math

def event_timepoint_toS(timestr):
    str_ls = timestr.split(":")
    hour = str_ls[0]
    minute = str_ls[1]
    sec = str_ls[2]
    rt = int(hour) * 60 * 60 + int(minute) * 60 + float(sec)
    return rt


def exploration_plotting(idm_id,day_ls=None):
    current_dir = os.getcwd()
    idm_id_folder = "IDM"+str(idm_id)
    idm_path = os.path.join(current_dir,"data", idm_id_folder)
    file_ls = os.listdir(idm_path)
    file_ls = [x for x in file_ls if ("event" in x) and (".xlsx" in x)]
    if day_ls == None:
        file_days_ls = file_ls
    else:
        file_days_ls = [x for x in file_ls if x.split("_")[1] in day_ls]
    concat_ls=[]
    for file in file_ls:
        data_info = pd.read_excel(os.path.join(idm_path, file))
        concat_ls.append(data_info)
    data_all = pd.concat(concat_ls)
    mouse_ls = data_all["RFID"].unique().tolist()
    mouse_ls = [x for x in mouse_ls if len(x)==4]

    color_ls = ["lightcoral","mediumseagreen","wheat","lightblue","mediumpurple","gray"]
    id_color_dict={}
    for i in range(len(mouse_ls)):
        id_color_dict[mouse_ls[i]]=color_ls[i]

    print(idm_id_folder)
    print(id_color_dict)

    for file in file_days_ls:
        data_info = pd.read_excel(os.path.join(idm_path, file))
        date_key = file.split("_event")[0]

        exp_start = data_info["exp_starttime"][0]
        exp_start_S = event_timepoint_toS(exp_start)

        exp_end = data_info["exit_time"][data_info.index[-1]]
        exp_end_S = event_timepoint_toS(exp_end)


        plt.figure(figsize=(10, 3))
        for i in range(data_info.shape[0]):
            enter_time = data_info["enter_time"][i]
            enter_S = event_timepoint_toS(enter_time)-exp_start_S
            exit_time = data_info["exit_time"][i]
            exit_S = event_timepoint_toS(exit_time)-exp_start_S
            mouse = data_info["RFID"][i]
            if mouse in mouse_ls:
                plt.axvspan(enter_S,exit_S,color=id_color_dict[mouse])
            else:
                plt.axvspan(enter_S,exit_S,color="black")
        plt.xlim([0,exp_end_S-exp_start_S])

        plt.xlabel("Time(min)", fontsize=16)
        plt.xticks(np.linspace(0,9000,6),np.linspace(0,150,6))
        plt.title(date_key, fontsize=20)
        plt.tight_layout(pad=3)
        plt.show()


def exploration_times_bar_plotting(idm_id,day_ls=None):
    current_dir = os.getcwd()
    idm_id_folder = "IDM"+str(idm_id)
    idm_path = os.path.join(current_dir, "data", idm_id_folder)
    file_ls = os.listdir(idm_path)
    file_ls = [x for x in file_ls if ("event" in x) and (".xlsx" in x)]
    if day_ls == None:
        file_days_ls = file_ls
    else:
        file_days_ls = [x for x in file_ls if x.split("_")[1] in day_ls]
    concat_ls=[]
    for file in file_ls:
        data_info = pd.read_excel(os.path.join(idm_path, file))
        concat_ls.append(data_info)
    data_all = pd.concat(concat_ls)
    mouse_ls = data_all["RFID"].unique().tolist()
    mouse_ls = [x for x in mouse_ls if len(x)==4]

    color_ls = ["lightcoral","mediumseagreen","wheat","lightblue","mediumpurple","gray"]
    id_color_dict={}
    for i in range(len(mouse_ls)):
        id_color_dict[mouse_ls[i]]=color_ls[i]

    print(idm_id_folder)
    print(id_color_dict)

    for file in file_days_ls:
        data_info = pd.read_excel(os.path.join(idm_path, file))
        date_key = file.split("_event")[0]

        data_info = data_info[data_info["RFID"].isin(mouse_ls)]
        data_info = data_info.reset_index()

        exp_start = data_info["exp_starttime"][0]
        exp_start_S = event_timepoint_toS(exp_start)
        exp_end = data_info["exit_time"][data_info.index[-1]]
        exp_end_S = event_timepoint_toS(exp_end)
        total_S = exp_end_S-exp_start_S

        data_by_mouse=data_info.groupby("RFID").count()
        data_by_mouse.index.name = None
        data_by_mouse = data_by_mouse.reindex(mouse_ls,fill_value=0)
        data_by_mouse["norm_entrT"]=data_by_mouse.apply(lambda x:(x["enter_time"]/(total_S/60/60)),axis=1)
        mouse_order = data_by_mouse.index.tolist()
        color_order = [id_color_dict[x] for x in mouse_order]

        plt.figure(figsize=(3,3))
        plt.bar(mouse_order,data_by_mouse["norm_entrT"],color=color_order)
        plt.ylim([0,8])
        plt.ylabel("Visiting frequency(bouts/hour)")
        plt.xlabel("mouse ID")
        plt.xticks(rotation=90)
        plt.title(date_key) 
        plt.tight_layout(pad=3)
        plt.show()
        

def mean_exploration_duration_bar_plotting(idm_id,day_ls=None,sem=False):
    current_dir = os.getcwd()
    idm_id_folder = "IDM"+str(idm_id)
    idm_path = os.path.join(current_dir, "data", idm_id_folder)
    file_ls = os.listdir(idm_path)
    file_ls = [x for x in file_ls if ("event" in x) and (".xlsx" in x)]
    if day_ls == None:
        file_days_ls = file_ls
    else:
        file_days_ls = [x for x in file_ls if x.split("_")[1] in day_ls]
    concat_ls=[]
    for file in file_ls:
        data_info = pd.read_excel(os.path.join(idm_path, file))
        concat_ls.append(data_info)
    data_all = pd.concat(concat_ls)
    mouse_ls = data_all["RFID"].unique().tolist()
    mouse_ls = [x for x in mouse_ls if len(x)==4]

    color_ls = ["lightcoral","mediumseagreen","wheat","lightblue","mediumpurple","gray"]
    id_color_dict={}
    for i in range(len(mouse_ls)):
        id_color_dict[mouse_ls[i]]=color_ls[i]

    print(idm_id_folder)
    print(id_color_dict)

    for file in file_days_ls:
        data_info = pd.read_excel(os.path.join(idm_path, file))
        date_key = file.split("_event")[0]

        data_info = data_info[data_info["RFID"].isin(mouse_ls)]
        data_info = data_info.reset_index()

        exp_start = data_info["exp_starttime"][0]
        exp_start_S = event_timepoint_toS(exp_start)
        exp_end = data_info["exit_time"][data_info.index[-1]]
        exp_end_S = event_timepoint_toS(exp_end)
        total_S = exp_end_S-exp_start_S

        data_info["stayS"] = data_info.apply(lambda x:(event_timepoint_toS(x["exit_time"])-event_timepoint_toS(x["enter_time"])),axis=1)
        data_by_mouse=data_info.groupby("RFID").mean()
        data_by_mouse.index.name = None
        data_by_mouse = data_by_mouse.reindex(mouse_ls,fill_value=0)
        data_by_mouse["stayM_per_visit"]=data_by_mouse.apply(lambda x:(x["stayS"]/60),axis=1)
        mouse_order = data_by_mouse.index.tolist()
        color_order = [id_color_dict[x] for x in mouse_order]

        plt.figure(figsize=(3,3))
        plt.bar(mouse_order,data_by_mouse["stayM_per_visit"],color=color_order)
        if sem==True:
            sem_by_mouse = data_info.groupby("RFID").sem()
            sem_by_mouse.index.name = None
            sem_by_mouse = sem_by_mouse.reindex(mouse_ls,fill_value=0)
            sem_by_mouse["stayM_per_visit"]=sem_by_mouse.apply(lambda x:(x["stayS"]/60),axis=1)
            plt.errorbar(mouse_order,data_by_mouse["stayM_per_visit"],yerr=sem_by_mouse["stayM_per_visit"],fmt="none",
                         color="black",capsize=5)
        plt.ylabel("Average visiting duration(min)")
        plt.xlabel("mouse ID")
        plt.xticks(rotation=90)
        plt.title(date_key) 
        plt.tight_layout(pad=3)
        plt.show()
        
        
def social_exploration_plotting(idm_id,ds_pair):
    current_dir = os.getcwd()
    idm_id_folder = "IDM"+str(idm_id)
    idm_path = os.path.join(current_dir,"data", idm_id_folder)
    file_ls = os.listdir(idm_path)
    event_ls = [x for x in file_ls if ("event" in x) and (".xlsx" in x)]
    video_file = [x for x in file_ls if "videonames" in x][0]
    df_video = pd.read_csv(os.path.join(idm_path, video_file))

    color_ls = ["gold","gray"]
    id_color_dict={}
    for i in range(len(ds_pair)):
        id_color_dict[ds_pair[i]]=color_ls[i]
    print(id_color_dict)


    for file in event_ls:
        date_key = file.split("_")[1]
        data_info = pd.read_excel(os.path.join(idm_path, file))
        if "comment" in data_info.columns:
            data_info["comment"] = data_info["comment"].fillna("keep")
            data_info = data_info[data_info["comment"]=="keep"]
            data_info = data_info.reset_index()

        video_start_S = df_video[df_video["day"]==date_key]["video_start_S"].values[0]

        exp_start = data_info["exp_starttime"][0]
        exp_start_S = event_timepoint_toS(exp_start)
        exp_start_frame = int(math.ceil((exp_start_S - video_start_S) * 30))
        exp_end_frame = exp_start_frame + 2*60*60*30

        plt.figure(figsize=(10, 1))
        for i in range(data_info.shape[0]):
            enter_time = data_info["enter_time"][i]
            enter_S = event_timepoint_toS(enter_time)
            enter_frame = int(math.ceil((enter_S - video_start_S) * 30))
            exit_time = data_info["exit_time"][i]
            exit_S = event_timepoint_toS(exit_time)
            exit_frame = int(math.ceil((exit_S - video_start_S) * 30))
            mouse = str(data_info["RFID"][i])
            plt.axvspan(enter_frame,exit_frame,color=id_color_dict[mouse])
        plt.xlim([exp_start_frame,exp_end_frame])
        plt.xticks(np.linspace(exp_start_frame,exp_end_frame,5),np.linspace(0,120,5))
        plt.yticks([])
        plt.title("IDM"+str(idm_id)+" "+date_key,fontsize=15)
        plt.show()
        

def feature_table_processor(df_idm):
    df_idm["x_loc_distance_duration_high_speed"].fillna(0, inplace=True)
    df_idm["max_speedS"].fillna(0, inplace=True)
    df_idm["escape_distance"].fillna(0, inplace=True)
    df_idm["escape_max_acc"].fillna(0, inplace=True)
    df_idm["fastest_escape_start"].fillna(600, inplace=True)
    df_idm["latency_to_first_escape"].fillna(600, inplace=True)
    df_idm["durationsM"].fillna(0, inplace=True)
    df_idm["sum_duration_lsM"].fillna(0, inplace=True)
    df_idm["freeze_start"].fillna(600, inplace=True)
    df_idm["reach_safe_idx"].fillna(900, inplace=True)
    df_idm["x_loc_off_to_sz"] = df_idm.apply(lambda x: (1885 - x['x_loc_off']), axis=1)
    df_idm["x_loc_end_to_sz"] = df_idm.apply(lambda x: (1885 - x['x_loc_end']), axis=1)
    df_idm["x_loc_exit_to_sz"] = df_idm.apply(lambda x: (1885 - x['x_loc_exit']), axis=1)
    df_idm["x_loc_change"] = df_idm.apply(lambda x: (x['x_loc_end'] - x['x_loc_looming']), axis=1)
    df_idm["exit_time_after_looming"] = df_idm.apply(lambda x: (x['exit_idx'] - 300), axis=1)
    df_idm["end_time_after_looming"] = df_idm.apply(lambda x: (x['trial_end_idx'] - 300), axis=1)
    df_idm["reach_safe_time_after_looming"] = df_idm.apply(lambda x: (x['reach_safe_idx'] - 300), axis=1)
    df_idm["escape_to_reach_safe_time"] = df_idm.apply(lambda x: (x['reach_safe_idx'] - 300 - x['latency_to_first_escape']), axis=1)
    df_idm["first_decision"] = df_idm.apply(lambda x: (1 if x['latency_to_first_escape']<x['freeze_start'] else 2), axis=1)

    return df_idm


def feature_unit_scaling(df_idm):
    # speed already scaled at preprocessing
    fps = 30
    cmPerPixel = 100/1885
    df_new = df_idm.copy(deep=True)
    df_cols = df_idm.columns
    time_related_feature = ['latency_to_maxSpeed', 'duration_high_speed','exit_time_after_looming',"longest_immobile_duration",
                            "first_immobile_start","total_immobile_duration",
                            "end_time_after_looming","escape_to_reach_safe_time","duration_reward",
                            "reach_safe_time_after_looming", 'durationsM', "sum_duration_lsM",
                            'fastest_escape_start', 'freeze_start','first_freeze_duration', 'freeze_end',
                            "decision_latency","decision_latency_new",
                            'duration_between_escape_and_freeze', "exit_time_after_looming",'latency_to_first_escape',
                           'back_idx_after_flee']
    distance_related_feature = ['x_loc_looming', 'x_loc_off', 'x_loc_end','x_loc_exit', "x_loc_off_to_sz","x_loc_end_to_sz",
                                "x_loc_exit_to_sz",'x_loc_distance_duration_high_speed',
                                'escape_distance', "x_loc_change", "x_loc_immobile","furthest_loc","nearest_back_loc",
                               "furthest_loc_after_esc","nearest_back_loc_after_esc",]
    for f_time in time_related_feature:
        if f_time in df_cols:
            df_new[f_time] = df_idm.apply(lambda x: x[f_time] / fps, axis=1)
        else:
            continue
    for f_dis in distance_related_feature:
        if f_dis in df_cols:
            df_new[f_dis] = df_idm.apply(lambda x: x[f_dis] * cmPerPixel, axis=1)
        else:
            continue
    return df_new


def plot_speed_heatmap(data_scaled, df_info, plot_name, order="trial", plotsize=(10,5), see_title=True):
    data_by_trial= data_scaled.groupby("trial_index")
    index_ls = data_scaled["trial_index"].unique()
    inter_table = pd.DataFrame(columns=range(900),index=index_ls)
    plt.figure(figsize=plotsize)
    for trial, window_data in data_by_trial:
        sample_data = window_data["speed_tailbase"].tolist()
        enter_idx = df_info.loc[df_info["trial_index"] == str.lower(trial), "enter_idx"]
        enter_idx = int(enter_idx.values[0])
        inter_table.loc[trial,enter_idx:len(sample_data)-1] = sample_data[enter_idx:]
    if order != "trial":
        trial_plot_ls = inter_table.index.tolist()
        latency_ls = []
        for t in trial_plot_ls:
            lat_time = df_info.loc[df_info["trial_index"] == str.lower(t), order]
            lat_time = lat_time.values[0]
            latency_ls.append(lat_time)
        sorted_trial_ls = sorted(trial_plot_ls, key=lambda x: latency_ls[trial_plot_ls.index(x)])
        inter_table = inter_table.reindex(index=sorted_trial_ls)
    print(inter_table.index.tolist())
    inter_table = inter_table.replace(pd.NA, np.nan)
    inter_table=pd.DataFrame(inter_table,dtype=np.float64)
    nrow = inter_table.shape[0]
    ax = sns.heatmap(inter_table,cmap = "bwr",vmin=-40,vmax=80,center=0, cbar_kws={"pad": 0.015})
    loom_point = np.linspace(300, 516, 10)
    plt.vlines(loom_point, -20, 100, linestyles="dashed", color="black")
    plt.vlines([540], -20, 100, linestyles="solid", color="black")
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=15)
    cbar.ax.yaxis.set_tick_params(width=2, length=10)
    plt.yticks([])
    plt.xticks([0,299,599,899],["-10","0","10","20"],size=15,rotation="horizontal")
    plt.tight_layout(pad=3)
    if see_title:
        plt.title(plot_name, fontsize=20)
    plt.show()
    
    
def plot_loc_line_over_trials(data_scaled, plot_name, water_line=True,
                              plotsize=(10,5), see_title=True):
    data_scaled["dis_to_safezone"] = data_scaled.apply(lambda x: 100-x["tailbase_x"], axis=1)
    data_by_trial = data_scaled.groupby("trial_index")
    plt.figure(figsize=plotsize)
    for trial, window_data in data_by_trial:
        sample_data = window_data.reset_index()
        plt.plot(sample_data["dis_to_safezone"][11:], color="black")
    plt.xlim(0,900)
    plt.ylim(-20,100)
    plt.yticks([0,20,40,60,80,100],size=15)
    plt.xticks([0,300,600,900],["-10","0","10","20"],size=15)
    ax=plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_linewidth(2)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(2)
    ax.set_ylabel('Distance to safe zone [cm]', fontsize=16)
    ax.set_xlabel('Time (s)', fontsize=16)
    loom_point = np.linspace(300, 516, 10)
    plt.vlines(loom_point, -20, 100, linestyles="dashed", color="red")
    plt.vlines([540], -20, 100, linestyles="solid", color="red")
    if water_line:
        plt.hlines(100, 0, 900, linewidth=3, color="royalblue")
        plt.text(0, 100, "water", fontsize=15, color="royalblue", ha='left', va='bottom')
    plt.fill_between([0, 900], -20, 0, facecolor='gray', alpha=0.8)

    plt.tight_layout(pad=3)
    if see_title:
        plt.title(plot_name, fontsize=20)
    plt.show()


def plot_loc_line_hist(data_scaled, df_processed, plot_name,water_line=True, plotsize=(10,5), see_title=True):
    data_scaled["dis_to_safezone"] = data_scaled.apply(lambda x: 100-x["tailbase_x"], axis=1)
    trial_ls = data_scaled["trial_index"].unique().tolist()
    df_need = df_processed[df_processed["trial_index"].isin(trial_ls)]
    
    plt.figure(figsize=plotsize)
    grid = plt.GridSpec(1,17,wspace=0.5) 
    main_ax = plt.subplot(grid[:,0:15])

    data_by_trial = data_scaled.groupby("trial_index")
    for trial, window_data in data_by_trial:
        sample_data = window_data.reset_index()
        final_idx = int(df_need.loc[df_need["trial_index"]==trial,"exit_idx"].tolist()[0])              
        plt.plot(sample_data["dis_to_safezone"][11:final_idx], color="black")      

    plt.xlim(0,900)
    plt.ylim(-20,100)
    plt.yticks([0,20,40,60,80,100],size=15)
    plt.xticks([0,300,600,900],["-10","0","10","20"],size=15)
    ax=plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_linewidth(2)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(2)
    ax.set_ylabel('Distance to safe zone [cm]', fontsize=16)
    ax.set_xlabel('Time (s)', fontsize=16)
    loom_point = np.linspace(300, 516, 10)
    plt.vlines(loom_point, -20, 100, linestyles="dashed", color="red",alpha=0.8)
    plt.vlines([540], -20, 100, linestyles="solid", color="red",alpha=0.8)
    if water_line:
        plt.hlines(100, 0, 900, linewidth=3, color="royalblue")
        plt.text(0, 100, "water", fontsize=15, color="royalblue", ha='left', va='bottom')
    plt.fill_between([0, 900], -20, 0, facecolor='gray', alpha=0.8)
    if see_title:
        plt.title(plot_name, fontsize=20)
    plt.tight_layout(pad=3) 
    y_hist = plt.subplot(grid[:,15:17],xticklabels=[],sharey=main_ax)
    bin_list = [-20,0,20,40,60,80,100]
    plt.hist(df_need["x_loc_exit_to_sz"],color="gray",edgecolor="black",orientation="horizontal",bins=bin_list)
    ax_h=plt.gca()
    ax_h.get_xaxis().set_visible(False)
    ax_h.get_yaxis().set_visible(False)

    plt.show() 

    
def plot_mean_sem_feature_curve(df_idm, vary="num_stim", feature="max_speedS", shelter=0, xrange="default",yrange="default"):
    if shelter == 0:
        df_need = df_idm
    else:
        df_need = df_idm[df_idm["num_stim"] <= shelter]
    min_value = df_need[feature].min()
    max_value = df_need[feature].max()
    max_vary = df_need[vary].max()
    dc_vary_group = df_need.groupby(vary)
    mean_value = dc_vary_group.mean()
    sem_value = dc_vary_group.sem()
    plt.figure(figsize=(4, 3))
    if yrange == "default":
        plt.ylim([min_value-0.05, max_value + 0.05])
    else:
        plt.ylim(yrange)
    if xrange == "default":
        plt.xlim([0, max_vary+0.05])
    else:
        plt.xlim(xrange)
    plt.plot(mean_value.index, mean_value[feature],"-o",color="black")
    plt.fill_between(mean_value.index, mean_value[feature]-sem_value[feature], mean_value[feature]+sem_value[feature],
                     color='gray', alpha=0.2)
    plt.ylabel(feature)
    plt.xlabel(vary)
    plt.title(feature)
    plt.tight_layout()
    plt.show()

    
def adjacent_values(vals, q1, q3):
    upper_adjacent_value = q3 + (q3 - q1) * 1.5
    upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])

    lower_adjacent_value = q1 - (q3 - q1) * 1.5
    lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
    return lower_adjacent_value, upper_adjacent_value


def violin_plot(x,ax,pos=1,facecolor='orange',median_color='white',mean_color='blue',vert=True):
    parts = ax.violinplot(
        x, [pos], showmeans=False, showmedians=False, vert=vert,
        showextrema=False, points=200)
    for pc in parts['bodies']:
        pc.set_facecolor(facecolor)
        pc.set_edgecolor('black')
        pc.set_linewidth(0.5)
        pc.set_alpha(1)
        
    quartile1, medians, quartile3 = np.percentile(x, [25, 50, 75], axis=0)
    whiskers = np.array([adjacent_values(sorted(x), quartile1, quartile3)])
    whiskers_min, whiskers_max = whiskers[:, 0], whiskers[:, 1]
    inds = np.arange(pos, pos+1)
    means = np.mean(x,axis=0)
    if vert == False:
        ax.scatter(medians, inds, marker='o', color=median_color,edgecolor='black',linewidths=0.5,s=50, zorder=3)
        ax.vlines(means,inds[0]-0.1,inds[0]+0.1,color=mean_color, linestyle='-',lw=1,zorder=3)
        ax.hlines(inds, quartile1, quartile3, color='black', linestyle='-', lw=1.5)
        ax.hlines(inds, whiskers_min, whiskers_max, color='black', linestyle='-', lw=0.5)
    elif vert == True:
        ax.scatter(inds, medians, marker='o', color=median_color,edgecolor='black',linewidths=0.5, s=50, zorder=3)
        ax.hlines(means,inds[0]-0.1,inds[0]+0.1,color=mean_color, linestyle='-',lw=1,zorder=3)
        ax.vlines(inds, quartile1, quartile3, color='black', linestyle='-', lw=1.5)
        ax.vlines(inds, whiskers_min, whiskers_max, color='black', linestyle='-', lw=0.5)
    
    
def prism_quartiles(data):
    data_sorted = sorted(data)
    n = len(data_sorted)

    median = np.median(data_sorted)

    if n % 2 == 1:
        lower_half = data_sorted[:n//2]
        upper_half = data_sorted[n//2 + 1:]
    else:
        lower_half = data_sorted[:n//2]
        upper_half = data_sorted[n//2:]

    q1 = np.median(lower_half) if len(lower_half) > 0 else median
    q3 = np.median(upper_half) if len(upper_half) > 0 else median

    return q1, median, q3


def prism_boxplot(data,ax,center=1,box_width=0.5, edgecolor="black"):
    q1, median, q3 = prism_quartiles(data)
    minimum = min(data)
    maximum = max(data)
    
    rect = patches.Rectangle(
        (center - box_width/2, q1),
        box_width,
        q3 - q1,
        facecolor='none',
        edgecolor=edgecolor
    )
    ax.add_patch(rect)

    # median
    ax.plot(
        [center - box_width/2, center + box_width/2],
        [median, median],
        color=edgecolor,
        linewidth=2
    )
    # whisker line
    ax.plot([center, center], [minimum, q1], color=edgecolor)
    ax.plot([center, center], [q3, maximum], color=edgecolor)

    # whisker caps
    cap_width = box_width * 0.4
    ax.plot([center - cap_width/2, center + cap_width/2], [minimum, minimum], color=edgecolor)
    ax.plot([center - cap_width/2, center + cap_width/2], [maximum, maximum], color=edgecolor)

    
# Defining a fitting fucntionß
def hab_exp(x,tau_1,tau_2):
    x = x-1
    return (np.exp(-x/tau_1)+np.exp(-x/tau_2))/2


def weber(sc,sc_0):
    pc = np.zeros_like(sc)
    if sc>=sc_0:
        pc = np.log(sc/sc_0)/np.log(1/sc_0)
    return pc


def cos_dist(x,y):
    return (1-np.dot(x,y.T)/(np.linalg.norm(x)*np.linalg.norm(y)))/2

        
def savefig(file_save):
    plt.savefig(file_save+'.png',bbox_inches='tight')
    plt.savefig(file_save+'.svg',bbox_inches='tight')
    plt.savefig(file_save+'.pdf',bbox_inches='tight')
    
    
def pie_plot(decisions,decisions_fit,file_save=''):
    fig,axs = plt.subplots(2,2)
    axs[0,0].pie([decisions[0][2],decisions[0][1],decisions[0][0]],labels=['flee','asse+flee','NR'],colors=['crimson','orange','mediumseagreen'])
    axs[0,1].pie([decisions[1][2],decisions[1][1],decisions[1][0]],labels=['flee','asse+flee','NR'],colors=['crimson','orange','mediumseagreen'])
    
    axs[1,0].pie([decisions_fit[0][2],decisions_fit[0][1],decisions_fit[0][0]],
                 labels=['flee','asse+flee','NR'],colors=['crimson','orange','mediumseagreen'])
    axs[1,1].pie([decisions_fit[1][2],decisions_fit[1][1],decisions_fit[1][0]],
                 labels=['flee','asse+flee','NR'],colors=['crimson','orange','mediumseagreen'])
    if len(file_save)>0:
        savefig(file_save)
    plt.show()
    
    
def plot_sem(t,y,ye,context,fig_size_unit=6,file_save=''):
    vs_start = context["vs_start"]
    time_before = context["time_before"]
    fig,ax = plt.subplots(1,1,figsize=(fig_size_unit,fig_size_unit*0.618))
    ax.plot(t,y, color='black')   
    ax.fill_between(t, y-ye, y+ye, color='grey')
    for xc in vs_start:
        plt.axvline(x=xc+time_before,color='red',ls='--',alpha=0.5)
    plt.xticks(np.arange(2, 22, step=5),np.arange(0, 20, step=5))
    plt.ylim([-0.3,1.7])
    plt.yticks(np.arange(0, 2, step=0.5))
    if len(file_save)>0:
        savefig(file_save)
    plt.show()
    
    
def plot_trials(t,y,fig_size_unit=6,file_save=''):
    fig,ax = plt.subplots(1,1,figsize=(fig_size_unit,fig_size_unit*0.618))
    n_t = y.shape[-1]
    ax.plot(t,np.reshape(y,(-1,n_t)).T, color='grey',linewidth=0.2)   
    ax.plot(t,np.mean(y,axis=(0,1)), color='black',linewidth=0.5)   
    ax.axhline(0.6, ls='dashed', color='green',linewidth=0.5)
    ax.axhline(0, ls='dashed', color='blue',linewidth=0.5)
    plt.xticks(np.arange(2, 22, step=5),np.arange(0, 20, step=5))
    ax.tick_params(width=0.5)
    for spine in ["top","right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["bottom","left"]:
        ax.spines[spine].set_linewidth(0.5)
    ax.set_axisbelow(True)
    if len(file_save)>0:
        savefig(file_save)
    plt.show()
    

def plot_latency(latency,context,fig_size_unit=6,file_save=''):
    vs_start = context["vs_start"]
    plt.figure(figsize=(fig_size_unit,fig_size_unit*0.618))
    plt.hist(latency,bins=np.arange(0,10.2,0.2),color='grey',edgecolor='black',linewidth=0.5)
    for xc in vs_start:
        plt.axvline(x=xc,color='red',ls='--',lw=0.5,alpha=0.5)
    plt.axvline(x=np.nanmedian(latency),color='green',ls='-',lw=0.7,alpha=0.8)
    plt.xlabel('latency to flee (s)',fontsize=18)
    plt.ylabel('trial count',fontsize=18)
    plt.xlim([-0.2,10.2])
    ax=plt.gca()
    for spine in ["top","right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["bottom","left"]:
        ax.spines[spine].set_linewidth(0.5)
    ax.set_axisbelow(True)
    if len(file_save)>0:
        savefig(file_save)  
    plt.show()


def plot_speed(peak_speed,fig_size_unit=6,):
    peak_speed[peak_speed<0]=0
    plt.figure(figsize=(fig_size_unit,fig_size_unit*0.618))
    dt = 0.05
    plt.hist(peak_speed,bins=np.arange(0.6,2,dt),color='grey',edgecolor='black')
    plt.axvline(x=np.nanmedian(peak_speed),color='blue',ls='-')
    plt.xlim([0.6,1.7])
    plt.xlabel('peak_speed',fontsize=18)
    plt.ylabel('trial count',fontsize=18)
    plt.show()


def hab_exp_fit(params,x,y):
    tau_1 = params['tau_1']
    tau_2 = params['tau_2']
    x = x-1
    y_fit = (np.exp(-x/tau_1)+np.exp(-x/tau_2))/2
    return y-y_fit


def value_fun_fit_1st_plot(params, contrast, context):
    alpha = params['alpha']
    thr_flee = params['thr_flee']
    beta_low = 1
    beta_high = params['beta_high']
    beta_arr = np.array([beta_low, beta_high])
    delta_noise = params['delta_noise']

    vs = context["vs"]
    t = context["t"]
    dt = context["dt"]
    n_t = context["n_t"]
    time_before = context["time_before"]
    trials_reward = context["trials_reward"]
    hab_tau_1 = context["hab_tau_1"]
    hab_tau_2 = context["hab_tau_2"]
    
    print('{:.2f},{:.2f},{:.2f},{:.2f}'.format(alpha,thr_flee,beta_high,delta_noise))
    hab_arr=hab_exp(trials_reward,hab_tau_1,hab_tau_2)
    n_hab = hab_arr.size
    value = np.zeros(n_t)
    reward = 0 
    latency_flee_sd_fit = np.zeros_like(contrast)
    n_rep = 100
    latency_flee_fit = np.zeros((2,n_hab,n_rep))
    decisions_fit = np.zeros((2,n_hab,n_rep))
    decisions_fit_sum = np.zeros((2,3))
    value_arr = np.zeros((2,n_hab,n_rep,n_t))
    rand_seeds = []
    for ci, c in enumerate(contrast):
        plt.figure()
        beta = beta_arr[ci]
        for i_hab,hab in enumerate(hab_arr): 
            for i_rep in range(n_rep):
                value = np.zeros(n_t)
                np.random.seed(i_rep+i_hab*n_rep+ci*n_rep*n_hab)
                rand_seeds.append(i_rep+i_hab*n_rep+ci*n_rep*n_hab)
                noise = (np.random.rand(n_t)*2-1)
                for i in range(1,n_t):
                    d_value = (-value[i-1]*alpha + beta*hab*vs[i] - reward + delta_noise*noise[i])*dt
                    value[i] = value[i-1] + d_value
                plt.plot(value,alpha=0.5)
                value_arr[ci,i_hab,i_rep,:] = value
                if np.sum(value>thr_flee) == 0:
                    latency_flee_fit[ci,i_hab,i_rep] = np.nan
                    decisions_fit[ci,i_hab,i_rep] = 0
                else:
                    latency_flee_fit[ci,i_hab,i_rep] = t[value>thr_flee][0]-time_before
                    if latency_flee_fit[ci,i_hab,i_rep] >= 0.8: 
                        decisions_fit[ci,i_hab,i_rep] = 1
                    else:
                        decisions_fit[ci,i_hab,i_rep] = 2
        latency_flee_fit[latency_flee_fit<0] = 0       
        decisions_fit_sum[ci,0] = np.sum(decisions_fit[ci,:,:]==0)/(n_hab*n_rep)
        decisions_fit_sum[ci,1] = np.sum(decisions_fit[ci,:,:]==1)/(n_hab*n_rep)
        decisions_fit_sum[ci,2] = np.sum(decisions_fit[ci,:,:]==2)/(n_hab*n_rep)
    return latency_flee_fit,decisions_fit_sum,value_arr,np.array(rand_seeds)


def value_fun_fit_2nd_plot(params, contrast, context):
    alpha = params['alpha']
    thr_flee = params['thr_flee']
    delta_noise = params['delta_noise']
    reward = params['reward']
    beta_low = params['beta_low']
    beta_high = params['beta_high']
    beta_arr = np.array([beta_low, beta_high])

    vs = context["vs"]
    t = context["t"]
    dt = context["dt"]
    n_t = context["n_t"]
    time_before = context["time_before"]
    trials_reward = context["trials_reward"]
    hab_tau_1 = context["hab_tau_1"]
    hab_tau_2 = context["hab_tau_2"]
    
    print('parameters: {:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}'.format(alpha,thr_flee,delta_noise,reward,beta_low,beta_high))
    hab_arr=hab_exp(trials_reward,hab_tau_1,hab_tau_2)
    n_hab = hab_arr.size
    value = np.zeros(n_t)  
    n_rep = 100
    latency_flee_fit = np.zeros((2,n_hab,n_rep))
    decisions_fit = np.zeros((2,n_hab,n_rep))
    decisions_fit_sum = np.zeros((2,3))
    vigor_fit = np.zeros((2,n_hab,n_rep))
    value_arr = np.zeros((2,n_hab,n_rep,n_t))
    for ci, c in enumerate(contrast):
        plt.figure()
        beta = beta_arr[ci]
        for i_hab,hab in enumerate(hab_arr): 
            for i_rep in range(n_rep):
                value = np.zeros(n_t)
                np.random.seed(i_rep+i_hab*n_rep+ci*n_rep*n_hab)
                noise = (np.random.rand(n_t)*2-1)
                for i in range(1,n_t):
                    d_value = (-value[i-1]*alpha + beta*hab*vs[i] - reward + delta_noise*noise[i])*dt
                    value[i] = value[i-1] + d_value
                plt.plot(value)
                value_arr[ci,i_hab,i_rep,:] = value
                if np.sum(value>thr_flee) == 0:
                    latency_flee_fit[ci,i_hab,i_rep] = np.nan
                    decisions_fit[ci,i_hab,i_rep] = 0
                else:
                    latency_flee_fit[ci,i_hab,i_rep] = t[value>thr_flee][0]-time_before
                    if latency_flee_fit[ci,i_hab,i_rep] >= 0.8: 
                        decisions_fit[ci,i_hab,i_rep] = 1
                    else:
                        decisions_fit[ci,i_hab,i_rep] = 2
        latency_flee_fit[latency_flee_fit<0] = 0       
        decisions_fit_sum[ci,0] = np.sum(decisions_fit[ci,:,:]==0)/(n_hab*n_rep)
        decisions_fit_sum[ci,1] = np.sum(decisions_fit[ci,:,:]==1)/(n_hab*n_rep)
        decisions_fit_sum[ci,2] = np.sum(decisions_fit[ci,:,:]==2)/(n_hab*n_rep)
        
    return latency_flee_fit,decisions_fit_sum,value_arr,vigor_fit