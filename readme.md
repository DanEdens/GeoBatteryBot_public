# Geo-Instruments Battery Tracker  

This [repo](https://github.com/DanEdens/Battery-Project) contains the tools for tracking movement of Batterys between Field deployments, Desulfating, and Inventory.  

---
> The project is currently in ***Production*** as LVP.  
> As of 6/27/2022, 52 batteries are in rotation.  

---
# Description  

This project aims to provide data to prevent the repeated deployment of worn out batterys.  

This is accomplished in 3 parts.  
1. QR code label generator - Written in Python  
2. Tablet App - Built on the Tasker framework, using Javascript  
3. Database running on an AWS Ec2 server running Ubuntu, and utilizing Mqtt  Node-red.  


## Module 1: Qr-code generation  
> QR-code stickers can be generated using [qr-generator.py](./qr-generator.py).  
> They are created using a first and last ID, and arranged  
> for easy importing into Brady Workstation to be printed.  

### Setup:
Clone the repo to your local machine.
run pip install requirements


---
## Module 2: Tablet App  
> Display and edit Battery Logs  
> Adds Notes and voltage readings to logs  
> Webhook server  

---
## Module 3: Database
> Manages Mqtt broker  
> Redundantly stores data incase of Tablet destruction  

---






---
# Roadmap:  

### 1. Color codes  
Add last-updated timestamp checks to visually display a batteries readiness status.  

> #### TODOs:  
> 1. Retrieve date from bottom line of log file  
> 1. Function to check if date is within 14 day desulfating window  

### 2.  Webportal  
Find solution for hosting and viewing log data via web.  
> #### TODOs:  
> 1. decide on either nodejs embedded in HTML, or node-red UI  


### 3. Vortex Intergration  
Find solution for importing battery data in Vortex  
> #### TODOs:  
> 1. Vortex Admin  
> 1. setup battery table  
> 1. webhooks for table importing  
---
# Dependencies  

These are the tools  

### Label Printer  
[BBP35(37) Label Printer](https://www.bradyid.com/label-printers/bbp35)  
[Brady workstation - Custom designer lite](https://workstation.bradyid.com/)  

### Python libraries  
[Wand](https://pypi.org/project/Wand/)  
[Pyqrcode](https://pypi.org/project/PyQRCode/)  

### Android:  
[Join](https://joaoapps.com/join/)  
[Tasker](https://tasker.joaoapps.com/)  
[Mqtt Client](https://play.google.com/store/apps/details?id=in.dc297.mqttclpro&hl=en_US&gl=US)  

### NodeJS  
[PM2]([https://pm2.keymetrics.io/)  
[Eclipse Mosquitto](https://mosquitto.org/)  
[AWS Ec2](https://en.wikipedia.org/wiki/Amazon_Elastic_Compute_Cloud)  
[Node Red](https://nodered.org/)  

---

# Run arguments

These are the currently availble CLI flags and Enviroment variables.  
Values will be used according to the following priority:  
1. CLI flag  
2. Environmment variable  
3. Input Query or Default  

---

### FirstID: '-F', '--firstID'  
> - Description:  
>   First Battery ID to generate.  
> - Type: *Int*  
> - Override Variable:  
>   *%BATTERYBOT_FIRSTID%*

### LastID: '-L', '--lastID'  
> - Description:  
> Last Battery ID to generate.  
> - Type: *Int*  
> - Override Variable:  
>   *%BATTERYBOT_LASTID%*

### Show: '-s', '--show'  
> - Description:  
> Open generated Image in system default photo viewer
> - Type: *Bool*  
> - Override Variable:  
>   *%BATTERYBOT_SHOW%*

### Log: '--log'  
> - Description:  
> Publish log message containing ID's used during generation to Mqtt broker  
> - Type: *Bool*  
> - Override Variable:  
>   *%BATTERYBOT_LOG%*

### Output: '-o', '--output'  
> - Description:  
>   Directory to output Label files.  
> - Default location: *"%CD%\\_output"*  
> - Type: *Str(Path)*  

### Show: '-s', '--show'  
> - Description:  
> Open generated Image in system default photo viewer.  
> - Type: *Bool*  
> - Override Variable:  
>   *%BATTERYBOT_SHOW%*

### Skip Clean up: '--nocleanup'  
> - Description:  
>   Prevents Clean up of temp files for debug purposes.  
> - Type: *Bool*  
> - Override Variable:  
>   *%BATTERYBOT_CLEANUP%*

### Show: '-c', '--clip'  
> - Description:  
>   Copy filepath to clipboard for importing into Brady workstation  
> - Type: *Bool*  
> - Override Variable:  
>   *%BATTERYBOT_CLIP%*  
