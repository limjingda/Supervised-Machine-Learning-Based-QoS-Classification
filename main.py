# Load libraries
import sys

import pandas as pd
import numpy as np
import math



col_names = ['No.',	'Time',	'Source IP', 'Src Port', 'Dest IP',	'Dest Port', 'Length', 'Info', 'Protocol']
network_req = pd.read_csv("teleop2.csv", names=col_names)


def assign_label(row):
    if ((row['Dest Port'] == '5000' or (row['Src Port'] == '5000')) and
        (row['Length'] == '1442'or '54') and
        (row['Protocol'] == 'TCP') ):
            return '1' ##upnp

    elif ((row['Src Port'] == '50520' or (row['Dest Port'] == '50520')) and
        (row['Length'] == '770' or '54') and
        (row['Protocol'] == 'TCP') ):
            return '2' ##Monitoring

    elif ((row['Dest Port'] == '50519' or (row['Src Port'] == '50519')) and
        (row['Length'] == '60' or '130') and
        (row['Protocol'] == 'TCP') ):
            return '3' ##Robot Control

    else:
        return '0'

network_req['label'] = network_req.apply(assign_label, axis=1)

network_req['Length'] = pd.to_numeric(network_req['Length'], errors='coerce')
network_req['Time'] = pd.to_numeric(network_req['Time'], errors='coerce')

df_upnp = network_req[network_req['label']=='1'].copy()
dfM = network_req[network_req['label']=='2'].copy()
dfr = network_req[network_req['label']=='3'].copy()

###### burst rate upnp #####
time_stamp = pd.to_numeric(df_upnp["Time"], errors='coerce')
df_upnp['Burst']= 0
interval_start = 0
interval_end = 1
while interval_end < len(df_upnp):
    if (time_stamp.iloc[interval_end] - time_stamp.iloc[interval_start]) >= 0.005:
        count = time_stamp.iloc[interval_start:interval_end].count()
        df_upnp['Burst'].iloc[interval_start:interval_end]=count
        interval_start = interval_end
        interval_end = interval_start +1

    elif interval_end == len(df_upnp) - 1:
        break
    else:
        interval_end +=1

###### burst rate monitoring #####
time_stamp = pd.to_numeric(dfM["Time"], errors='coerce')
dfM['Burst'] = 0
interval_start = 0
interval_end = 1
while interval_end < len(dfM):
    if (time_stamp.iloc[interval_end] - time_stamp.iloc[interval_start]) >= 0.005:
        count = time_stamp.iloc[interval_start:interval_end].count()
        dfM['Burst'].iloc[interval_start:interval_end] = count
        interval_start = interval_end
        interval_end = interval_start + 1
    elif interval_end == len(dfM) - 1:
        break
    else:
        interval_end += 1

# df.to_csv('BurstM.csv')
burst_combined = df_upnp[['Burst']].combine_first(dfM[['Burst']])


###### burst rate robot #####
time_stamp = pd.to_numeric(dfr["Time"], errors='coerce')
dfr['Burst'] = 0
interval_start = 0
interval_end = 1
while interval_end < len(dfr):
    if (time_stamp.iloc[interval_end] - time_stamp.iloc[interval_start]) >= 0.005:
        count = time_stamp.iloc[interval_start:interval_end].count()
        dfr['Burst'].iloc[interval_start:interval_end] = count
        interval_start = interval_end
        interval_end = interval_start + 1
    elif interval_end == len(dfr) - 1:
        break
    else:
        interval_end += 1
# df.to_csv('BurstRobot.csv')
burst_combined_2 = burst_combined[['Burst']].combine_first(dfr[['Burst']])
network_req['Burst'] = burst_combined_2

#### throughput monitoring ####
time_stamp = pd.to_numeric(dfM["Time"], errors='coerce')
packet_size = dfM["Length"]
dfM['Throughput']= 0

interval_start = 0
interval_end = 1
while interval_end < len(dfM):
    if interval_end == len(dfM):
        break

    elif (dfM.loc[time_stamp.index[interval_end], 'Time'] - dfM.loc[
        time_stamp.index[interval_start], 'Time']) >= 1.00000:
        tp = dfM.loc[packet_size.index[interval_start:interval_end - 1], 'Length'].sum()
        throughput = (tp * 8) / 1000000
        dfM.loc[time_stamp.index[interval_end - 1], 'Throughput'] = throughput

        if interval_end + 1 < len(dfM) and (dfM.loc[time_stamp.index[interval_end + 1], 'Time'] - dfM.loc[
            time_stamp.index[interval_start + 1], 'Time']) < 1.00000:
            tp = dfM.loc[packet_size.index[interval_start:interval_end + 1], 'Length'].sum()
            throughput = (tp * 8) / 1000000
            dfM.loc[time_stamp.index[interval_end], 'Throughput'] = throughput

        interval_start += 1
        interval_end = interval_start + 1
    else:
        interval_end += 1

##### throughput robot #####
time_stamp = pd.to_numeric(dfr["Time"], errors='coerce')
packet_size = dfr["Length"]
dfr['Throughput'] = 0

interval_start = 0
interval_end = 1

while interval_end < len(dfr):
    if interval_end == len(dfr):
        break

    elif (dfr.loc[time_stamp.index[interval_end], 'Time'] - dfr.loc[
        time_stamp.index[interval_start], 'Time']) >= 1.00000:
        tp = dfr.loc[packet_size.index[interval_start:interval_end - 1], 'Length'].sum()
        throughput = (tp * 8) / 1000000
        dfr.loc[time_stamp.index[interval_end - 1], 'Throughput'] = throughput

        if interval_end + 1 < len(dfr) and (dfr.loc[time_stamp.index[interval_end + 1], 'Time'] - dfr.loc[
            time_stamp.index[interval_start + 1], 'Time']) < 1.00000:
            tp = dfr.loc[packet_size.index[interval_start:interval_end + 1], 'Length'].sum()
            throughput = (tp * 8) / 1000000
            dfr.loc[time_stamp.index[interval_end], 'Throughput'] = throughput

        interval_start += 1
        interval_end = interval_start + 1
    else:
        interval_end += 1

tp_combined = dfM[['Throughput']].combine_first(dfr[['Throughput']])
network_req['Throughput'] = tp_combined


#### throughput upnp ####
df = network_req[network_req['label'] == '1'].copy()

# initialize 'Throughput' column with zeros
df['Throughput'] = 0

# initialize variables
interval_start = 0
interval_end = 1

while interval_end < len(df):
    # check if the time difference is >= 1 sec
    if (df.loc[df.index[interval_end], 'Time'] - df.loc[df.index[interval_start], 'Time']) >= 1:
        # calculate the throughput for the current interval
        tp = df.loc[df.index[interval_start:interval_end - 1], 'Length'].sum()
        throughput = (tp * 8) / 1000000
        df.loc[df.index[interval_start:interval_end - 1], 'Throughput'] = throughput

        # check if there is another packet in the next second
        if interval_end + 1 < len(df) and (
                df.loc[df.index[interval_end + 1], 'Time'] - df.loc[df.index[interval_start + 1], 'Time']) < 1:
            tp = df.loc[df.index[interval_start:interval_end], 'Length'].sum()
            throughput = (tp * 8) / 1000000
            df.loc[df.index[interval_end:interval_end + 1], 'Throughput'] = throughput

            # check if there are any subsequent packets with the same timestamp within the same second interval
            ts = df.loc[df.index[interval_end], 'Time']
            i = interval_end + 1
            while i < len(df) and df.loc[df.index[i], 'Time'] == ts:
                df.loc[df.index[i], 'Throughput'] = throughput
                i += 1

        # move to the next interval
        interval_start += 1
        interval_end = interval_start + 1

    else:
        # increment the interval end index
        interval_end += 1

tp_combined_2 = tp_combined[['Throughput']].combine_first(df[['Throughput']])
network_req['Throughput'] = tp_combined_2

network_req.to_csv('network_overview2.csv')


