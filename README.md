> 我们不推荐您使用该项目，建议转向由 SALTWOOD 开发的 [Open93@Home](https://github.com/SaltWood-Studio/Open93AtHome-V3) 项目<br>Tips: 推荐搭配由 Mxmilu666 开发的 [93Home-Dash](https://github.com/Mxmilu666/93Home-Dash) 一起运行。

<div align="center">
    <img src="https://socialify.git.ci/ZeroNexis/iodine-at-home/image?description=1&language=1&name=1&owner=1&theme=Auto" alt="iodine-at-home" width="640" height="320" />

# iodine@home

_✨ 开源的文件分发主控，并尝试兼容 OpenBMCLAPI 客户端 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/ZeroNexis/iodine-at-home.svg" alt="license">
</a>
<a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
</a>
</div>







## 📖 介绍

基于 [aiohttp](https://docs.aiohttp.org/) 和 [Socket.IO](https://socket.io/) 的 Python 文件分发主控。

## 🎉 运行

```shell
# 安装环境
pip install -r requirements.txt
 
# 运行主程序
python .\main.py
```

### 测试结果
基本完成，似乎能用？

## ⚙️ 配置

运行一次后，在`settings`目录下的的`.env`文件中添加下面的相关配置（请自行更改）

```
# 主配置
HOST = '0.0.0.0'
PORT = 8080
USERAGENT = 'iodine-ctrl/$version'
ACCESS_LOG = true

# 机密配置，请勿外传！！！
TOKEN = '123456'
JWT_SECRET = '114514'

# 证书配置
CERTIFICATES = false
CERT_PATH = './certificates/cert.pem'
KEY_PATH = './certificates/key.pem'

# 文件配置（使用英文逗号进行分隔）
GIT_REPOSITORY_LIST = "https://github.com/Mxmilu666/bangbang93HUB"
```

## 📖 许可证
本项目采用 `MIT License` 协议开源

## 💡 特别鸣谢

[**bangbang93**](https://github.com/bangbang93)
- [OpenBMCLAPI](https://github.com/bangbang93/openbmclapi) - 使用其 API 完成本项目与 OpenBMCLAPI 客户端的兼容。

[**8Mi_Yile**](https://github.com/8MiYile)
- 各种逆天言论，使 [bangbang93HUB](https://github.com/Mxmilu666/bangbang93HUB) 能持续更新至今，并给予我创建项目的灵感。

[**SALTWOOD**](https://github.com/SALTWOOD)
- [93@Home](https://github.com/SaltWood-Studio/Open93AtHome) - 提供了创建该项目的灵感及参考。
- [CSharp-OpenBMCLAPI](https://github.com/SaltWood-Studio/CSharp-OpenBMCLAPI) - 提供了 README 文件的参考。
- 回答了我提过的许多弱智问题，推动了项目的实现。
- 提供了原生实现 Avro 的部分代码。

[**tianxiu2b2t**](https://github.com/tianxiu2b2t)
- [python-openbmclapi](https://github.com/TTB-Network/python-openbmclapi) - 提供了原生实现 Avro 的部分代码。

[**Mxmilu666**](https://github.com/Mxmilu666)
- [bangbang93HUB](https://github.com/Mxmilu666/bangbang93HUB) - 提供了创建该项目的灵感。

[**群内的各位大佬们**](https://qm.qq.com/q/2OfvVrAwVG)（详细名单见贡献者列表）
- 参加我发出去的 Live Share，让项目更快得以实现。