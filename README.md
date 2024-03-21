# wtn-monitor
Wethenew monitor with automatic acceptance of offers and discord webhooks.

#Installation

##Windows

1. [Download](https://github.com/rudkarol/wtn-monitor/archive/refs/heads/main.zip) the latest release and unpack the .zip file
2. Make shure you have already installed python by typing `python --version` in cmd, if not [download the latest version for Windows](https://www.python.org/downloads/)
3. Go to unpacked directory and run: 
```
pip install -r requirements.txt
python main.py
```
4. Fill the `config.yaml`, `proxies.txt` and `wtn_acceptable.csv` files:
   - login to wtn and copy session cookie, paste it into `config.yaml`, remember not to refresh the page after copy the cookie
   - set your discord channel webhook url
   - set the delay to 2-10 sec
   - only `PID` and `MIN_PRICE` fields in `wtn_acceptable.csv` file are required, the other fields are for your use
5. Run the monitor:
```
python main.py
```

##Linux

1. [Download](https://github.com/rudkarol/wtn-monitor/archive/refs/heads/main.zip) the latest release and unpack the .zip file
2. Install `pip` by typing `sudo apt install python3-pip` in terminal
3. Go to unpacked directory and run: 
```
pip install -r requirements.txt
python3 main.py
```
4. Fill the `config.yaml`, `proxies.txt` and `wtn_acceptable.csv` files:
   - login to wtn and copy session cookie, paste it into `config.yaml`, remember not to refresh the page after copying the cookie
   - set your discord channel webhook url
   - set the delay to 2-10 sec
   - only `PID` and `MIN_PRICE` fields in `wtn_acceptable.csv` file are required, the other fields are for your use
5. Run the monitor:
```
python3 main.py
```
