# THE GAME CTF WRITE-UP
=====================

### Keep in mind, flag.txt has the answer for this room.

## This is my approach to solving the problem:
1. Download the task files
2. Use four commands: unzip, file, strings, and grep
3. Retrieve the flag

------------------------------------------------------------
## STEP 1: DOWNLOAD TASK FILES
------------------------------------------------------------

I downloaded the zip file containing Tetris.exe.
To unzip the file, I used:

    unzip XXX.zip

After unzipping, I obtained Tetris.exe.

------------------------------------------------------------
## STEP 2: CHECK FILE TYPE
------------------------------------------------------------

Since the file has an .exe extension, I didn’t want to take any risk running it directly.
I used the file command to check the actual type of the file:

    file Tetris.exe

Result:

    Tetris.exe: PE32+ executable for MS Windows 5.02 (GUI), x86-64 (stripped to external PDB), 13 sections

I don’t fully understand all the details, but it clearly indicates that it is an executable file.

To avoid any risk, I decided to use the strings command to retrieve human-readable text from the binary:

    strings Tetris.exe

Since there were many lines, I filtered the output using grep to find the flag:

    strings Tetris.exe | grep 'FLAG'

Note: I used single quotes around FLAG to ensure it is treated as a literal string, not a shell variable.

------------------------------------------------------------
## STEP 3: RETRIEVE THE FLAG
------------------------------------------------------------

Finally, the flag appeared:

    FLAG{example_flag_here}

Well done!

------------------------------------------------------------
## CONCLUSION
------------------------------------------------------------

- Using strings and grep allowed me to safely extract the flag without executing the .exe file.
- Always avoid running unknown executables directly to prevent potential security risks.