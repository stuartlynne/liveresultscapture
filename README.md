# liveresultscapture
# Sun Jun 29 10:46:37 AM PDT 2025


## Overview
*liveresultscapture* is a Python package to make a websocket connection to a running CrossMgr instance and capture live results. Results 
are captured in real-time and saved in *CSV* files.

Currently only CSV files are supported for export.

There is a mode to save the raw websocket messages in a JSON file, which can be useful for debugging.

The script will generate a new CSV file for every update it receives from *CrossMgr*.

The CSV files will be named based on the output path you provide. There are two options:

- a single CSV file per category
- a numbered CSV file per category, which will keep the last N files (default is 4, -1 to keep all files)

## TLS WebSockets

Both `ws://` and `wss://` URLs are supported. The `ws://` protocol is used for unencrypted connections, while `wss://` is used for encrypted connections (TLS/SSL).

When connecting to a CrossMgr instance, you should use the appropriate URL based on whether the instance is secured with TLS or not.
If you are connecting directly to a CrossMgr instance you will need to connect using a ws url:

```
ws://localhost:8766
ws://localhost
```

If you are connecting to a CrossMgr instance that is behind a reverse proxy, you will need to connect using a wss url:

```
ws://crossmgr.inthecloud.co:8766
ws://crossmgr.inthecloud.co
```

## Usage:
```
usage: live_csv_exporter [-h] [--save_json] [--save_numbered [SAVE_NUMBERED]]
                         [--version] [--verbose] [--quiet]
                         url output

Live CSV exporter for CrossMgr events

positional arguments:
  url                   WebSocket URL wss://example.com:8766 or
                        ws://localhost[:8766]
  output                Base output CSV path

options:
  -h, --help            show this help message and exit
  --save_json           Save messages in json file.
  --save_numbered [SAVE_NUMBERED]
                        Save numbered CSV files, keeping the last N files.
                        Default is 4. -1 to keep all files
  --version             show program's version number and exit
  --verbose             Verbose messages.
  --quiet               No messages.

Version: 0.1.0

Example: python3 live_csv_exporter.py ws://localhost[:8766] results.csv
The socket will default to 8766 if not specified.
```


## Output

### Notes:
1. Parenthesis around a lap time indicates an interpolated time. This would normally indicate either a missed chip read or, a trip to the pit with the rider taking a free lap.
```
Category,Pos,   Bib,                Name,                Team,   Time, Gap,    Speed,     Lap1,     Lap2,     Lap3,     Lap4,     Lap5,     
"All", "11" , 188  ,"Richard SCARBOROUG","SP Tableware Cyclin, "6:12",  -3,"29 km/h","(1:02)" ,"(1:02)" , "1:02"  , "1:03"  , "1:01"  , "0:60"  
```

2. Parenthesis around a position indicates that the last lap time was interpolated. This is *usually an error* and will disappear as soon as it is fixed or the rider finishes.
```
Category,Pos,   Bib,                Name,                Team,   Time, Gap,    Speed,     Lap1,     Lap2,     Lap3,     Lap4,     Lap5,     Lap6,     
"All","(15)", 212  ,"Sarah HEATH"       ,"Carmim-Prio"       , "7:54",  -3,"26 km/h", "1:07"  , "1:09"  , "1:07"  , "1:06"  , "1:07"  ,"(1:08)"
```

3. A negative number in the Gap column shows laps down. Those riders are almost always pulled, and the number will increase as the race progresses. 
```
Category,Pos,   Bib,                Name,                Team,   Time, Gap,    Speed,     Lap1,     Lap2,     Lap3,     Lap4,     Lap5,     
"All", "27" , 209  ,"Samantha SUMNER"   ,"BDC-Marcpol Team"  , "7:44",  -4,"22 km/h", "1:16"  , "1:18"  , "1:19"  , "1:21"  , "1:18"  
"All", "28" , 191  ,"Dominic BOWMAN"    ,"Team WIT?"         , "4:15",  -5,"28 km/h", "1:13"  , "0:53"  , "1:04"  , "1:04"  
"All", "29" , 185  ,"Seth PEARSON"      ,"Team Specialized Co, "0:60",  -8,"30 km/h", "0:60"  
```

4. DNF and DQ riders will be shown like this. Note, the DNF and DQ'd rider information is not always provided by the commissaires to the timing crew. 
```
Category,Pos,   Bib,                Name,                Team,   Time, Gap,    Speed,     Lap1,     Lap2,     
"All", "30" , 199  ,"Jesse STOUT"       ,"Metec Continental C, "0:55",   0,"32 km/h", "0:55"  ,"DNF"
"All", "31" , 192  ,"Antonio OLSEN"     ,"Alpha Baltic-Unitym, "0:00",   0,      "","DQ"
```

## Full CSV data for a simulated race:
```
Category,Pos,   Bib,                Name,                Team,   Time, Gap,    Speed,     Lap1,     Lap2,     Lap3,     Lap4,     Lap5
"All", "1"  , 187  ,"Blake GRAVES"      ,"Gios Deyser-Leon Ka, "8:19",   0,"32 km/h", "0:52"  , "0:55"  , "0:58"  , "0:58"  , "0:55"  
"All", "2"  , 193  ,"Jaden LOVE"        ,"Rietumu-Delfin"    , "9:36",17.0,"31 km/h", "0:57"  , "0:57"  , "0:59"  , "1:04"  , "0:55"  
"All", "3"  , 198  ,"Carson CHANDLER"   ,"Koga Cycling Team" , "9:36",17.0,"31 km/h", "0:56"  , "0:59"  , "0:56"  , "1:05"  , "0:57"  
"All", "4"  , 195  ,"Brayden CHRISTIAN" ,"Team Differdange-Ma, "9:43",24.2,"30 km/h", "0:60"  , "0:58"  , "0:57"  , "1:02"  , "1:03"  
"All", "5"  , 197  ,"Alejandro JAMES"   ,"Cycling Team Jo Pie, "9:43",24.2,"30 km/h","(0:59)" , "0:59"  , "0:55"  , "1:03"  , "0:57"  
"All", "6"  , 196  ,"Patrick LAMB"      ,"Cycling Team De Rij, "9:55",36.5,"30 km/h", "0:59"  , "0:58"  , "0:58"  , "1:10"  , "0:57"  
"All", "7"  , 189  ,"Carter SUTTON"     ,"Miche-Guerciotti"  , "9:11",52.3,"29 km/h", "1:00"  , "0:59"  , "1:00"  , "1:05"  , "1:08"  
"All", "8"  , 190  ,"Wyatt SINCLAIR"    ,"Team Idea"         , "9:11",52.3,"29 km/h", "1:02"  , "1:00"  , "1:01"  , "1:01"  , "0:58"  
"All", "9"  , 194  ,"Miguel MCLEAN"     ,"Leopard-Trek Contin, "8:20",  -1,"28 km/h", "0:60"  , "0:60"  , "1:02"  , "1:04"    
"All", "10" , 186  ,"Hayden RODGERS"    ,"Thüringer Energie T, "9:43",  -1,"27 km/h", "1:13"  , "1:03"  , "1:06"  , "1:03"    
"All", "11" , 188  ,"Richard SCARBOROUG","SP Tableware Cyclin, "6:12",  -3,"29 km/h","(1:02)" ,"(1:02)"     
"All", "12" , 211  ,"Alexis DAVIDSON"   ,"Wibatech-LMGK Ziemi, "7:33",  -3,"28 km/h", "1:03"  , "1:03"      
"All", "13" , 210  ,"Elizabeth CASSIDY" ,"CCC Polkowice"     , "7:47",  -3,"27 km/h", "1:07"  , "1:07"      
"All", "14" , 207  ,"Isabella MORSE"    ,"Team Øster Hus-Ridl, "7:50",  -3,"26 km/h", "1:07"  , "1:08"      
"All","(15)", 212  ,"Sarah HEATH"       ,"Carmim-Prio"       , "7:54",  -3,"26 km/h", "1:07"  , "1:09"      
"All", "16" , 208  ,"Ashley BOYKIN"     ,"Bank BGZ"          , "7:55",  -3,"26 km/h","(1:08)" , "1:08"      
"All", "17" , 213  ,"Alyssa BLANCHARD"  ,"Efapel-Glassdrive" , "7:59",  -3,"26 km/h", "1:07"  , "1:11"      
"All", "18" , 206  ,"Abigail TILLEY"    ,"Ringeriks-Kraft Loo, "7:04",  -3,"26 km/h", "1:10"  , "1:09"      
"All", "19" , 204  ,"Hannah CLAPP"      ,"Oneco-Mesterhus Cyc, "7:07",  -3,"25 km/h", "1:10"  , "1:10"      
"All", "20" , 200  ,"Tristan COWAN"     ,"Rabobank Continenta, "7:09",  -3,"25 km/h", "1:09"  , "1:12"      
"All", "21" , 203  ,"Emma BEASLEY"      ,"Team Joker Merida" , "7:11",  -3,"25 km/h", "1:12"  , "1:10"      
"All", "22" , 201  ,"Emily GOLDEN"      ,"Argon 18-Unaas Cycl, "7:16",  -3,"25 km/h", "1:08"  , "1:12"  "   
"All", "23" , 202  ,"Madison BOWLING"   ,"Frøy-Trek"         , "7:21",  -3,"25 km/h", "1:12"  , "1:11"    " 
"All", "24" , 214  ,"Grace MCALLISTER"  ,"LA-Antarte"        , "7:23",  -3,"24 km/h", "1:14"  , "1:10"      
"All", "25" , 215  ,"Sophia MCKENZIE"   ,"Onda"              , "7:25",  -3,"24 km/h","(1:13)" , "1:13"      
"All", "26" , 205  ,"Olivia ABRAMS"     ,"Plussbank BMC"     , "8:40",  -3,"24 km/h", "1:17"  ,"(1:15)"     
"All", "27" , 209  ,"Samantha SUMNER"   ,"BDC-Marcpol Team"  , "7:44",  -4,"22 km/h", "1:16"        
"All", "29" , 185  ,"Seth PEARSON"      ,"Team Specialized Co, "0:60",  -4,"30 km/h", "0:60"  
"All", "30" , 199  ,"Jesse STOUT"       ,"Metec Continental C, "0:55",   0,"32 km/h", "0:55"  ,"DNF"
"All", "31" , 192  ,"Antonio OLSEN"     ,"Alpha Baltic-Unitym, "0:00",   0,      "","DQ"
```


## Windows Defender and EXE

Pre-compiled versions of the script (using nuitka) are available.

This may be the preferred method of using this if you do not want to install Python.

N.b. Windows Defender sometimes flags these. There are two mitigations available:

- Pause Real-time protection
- Submit to Microsoft

### Pause Protection

1. Open the *Virus & threat protection settings* in Windows.
2. Click on *Manage settings*.
3. Click on the radio-button to disable *Real-Time protection*.

N.b. Pausing protection appears to timeout after about an hour or two.


### Submit file to Microsoft

Use this URL to submit the EXE to Microsoft.

[Microsoft Submit File](https://www.microsoft.com/en-us/wdsi/filesubmission)

Generally Microsoft will review in less than 24 hours and if they agree that the EXE
is not a threat will update their definitions.

### Typical Microsoft Response
```
At this time, the submitted files do not meet our criteria for malware or potentially unwanted applications. The detection has been removed. Please follow the steps below to clear cached detections and obtain the latest malware definitions.

1. Open command prompt as administrator and change directory to c:\Program Files\Windows Defender
2. Run “MpCmdRun.exe -removedefinitions -dynamicsignatures”
3. Run "MpCmdRun.exe -SignatureUpdate"

Alternatively, the latest definition is available for download here: https://docs.microsoft.com/microsoft-365/security/defender-endpoint/manage-updates-baselines-microsoft-defender-antivirus

Thank you for contacting Microsoft.

```

*N.b. After running the suggested commands it appears to take about a day for your local system
to stop flagging the EXE.*

