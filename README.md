# DIY-NAMIC-Analysis-For-Lazy-People
This script incorporates the original DIY-NAMIC Analysis code (from jhl0204) and DIY-NAMIC Latency code (from ssimonee).  It allows the user to perform DIY-NAMIC data ananlysis in one script.  This script also removed all the intermediate manual file rearrangement steps and user inputs that was required in the original DIY-NAMIC script. 


After downloading all the files into a folder, please run ""0_RunMe_Mac_Computer.py" or "0.RunMe_Windows_Comptuer.py" depending on which operating system you have.  These two programs only differ in one line of code due to the differences in "/" and "\\" formating between mac and windows comptuers.    

 file_name.append(full_path.split("/")[-1])  # Mac Comptuer
 
 file_name.append(full_path.split("\ \")[-1])  # PC comptuer
