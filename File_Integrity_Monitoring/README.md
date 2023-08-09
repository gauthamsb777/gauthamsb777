<h1>File Integrity Monitoring Tool</h1>

 
<h2>Description</h2>
This project consists of a simple Python script that monitors the integrity of the file using SHA-512 cryptographic hashing to compute and compare file hashes, establishing an initial baseline.txt that captures file paths and their corresponding hash values. the script's continous loop ensures its usability in realtime directory surveillance and any change detected is flaged through alert in the output.
<br />


<h2>Languages and Utilities Used</h2>

- <b>Python</b>
- <b>Python Interpreter/compiler</b>


<h2>Program walk-through:</h2>

<p align="center">
Execute the script and select the directory: <br/>
<img src="https://imgur.com/QzJ56Cu.png" height="80%" width="80%" alt="Disk Sanitization Steps"/>
<br />
<br />
Input y to start the hashing:  <br/>
<img src="https://imgur.com/tsJiHcL.png" height="80%" width="80%" alt="Disk Sanitization Steps"/>
<br />
<br />
Baseline will be generated: <br/>
<img src="https://imgur.com/QV3KEQ9.png" height="80%" width="80%" alt="Disk Sanitization Steps"/>
<br />
<br />
Any change is alerted:  <br/>
<img src="https://imgur.com/Zp3Y4Vs.png" height="80%" width="80%" alt="Disk Sanitization Steps"/>
<br />
<br />
Directory selection in linux based distro (kali linux):  <br/>
<img src="https://imgur.com/OBTFDxw.png" height="80%" width="80%" alt="Disk Sanitization Steps"/>
<br />
<br />
Results:  <br/>
<img src="https://imgur.com/jzgIA9F.png" height="80%" width="80%" alt="Disk Sanitization Steps"/>
<br />
<br />
ctrl z can be used to smoothly end the hashing:  <br/>
<img src="https://imgur.com/hkEfXVt.png" height="80%" width="80%" alt="Disk Sanitization Steps"/>
</p>

<!--
 ```diff
- text in red
+ text in green
! text in orange
# text in gray
@@ text in purple (and bold)@@
```
--!>


