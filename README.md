喜新厌旧
--------

### 安装

```
pipenv install --deploy
```

### 生成bash命令
使用 DNSPOD相关配置及AliCDN相关配置获取需要更新的域名信息, 生成脚本文件等待执行

```
python generate.py $DNSPOD_EMAIL $DNSPOD_TOKEN $CDN_ACCESS_ID $CDN_ACCESS_TOKEN $BASH_OUTPUT
```


### 执行bash命令
执行上一步生成的脚本文件

```
bash $BASH_OUTPUT
```
