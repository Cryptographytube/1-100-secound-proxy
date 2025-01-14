# 1-100-secound-proxy
## Features

- **Proxy Validation**: The script checks the validity of proxies using `httpbin.org/ip` to verify that the proxy is working.
- **Proxy Rotation**: Once a proxy is verified as active, it will be used in the rotation. Active proxies are set periodically in the `proxychains` configuration.
- **Environment Support**: The script supports both Termux (Android) and Kali Linux environments.
- **Continuous Monitoring**: The active proxies are continuously monitored and rotated, updating the configuration file for `proxychains`.

## Prerequisites

- Python 3.x installed
- Termux or Kali Linux installed (depends on your environment)
- Proxy list (`proxy_list.txt`) containing proxies in the format `IP:PORT`.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/proxy-rotation-script.git
cd proxy-rotation-script
pip install requests
python proxy-rotation.py
