# 云盘管理界的"政变"：AList被卖引发开源社区大逃亡，新王者OpenList强势崛起！

你有没有这样的经历：

手机里装了一堆云盘App——百度网盘、阿里云盘、夸克、OneDrive...每次找个文件都要挨个翻，像在玩"云盘大冒险"。

更崩溃的是，明明记得存了某个重要文件，但就是想不起来扔在哪个云盘里了。

这种"云盘焦虑症"，相信用过多个网盘的朋友都深有体会。

但最近，云盘管理工具界发生了一场堪比宫斗剧的"政变"，故事的转折比小说还精彩。

### 一场震惊开源圈的"背叛"

故事要从今年6月说起。

当时有个叫**AList**的开源项目，专门解决多云盘管理的痛点，能把30多种云存储服务整合到一个界面里，深受用户喜爱。

但突然有一天，社区炸锅了——原作者竟然**把项目卖了**！

![Alist被卖，社区集体叹息，新东家骚操作震惊全网_@Appinn_代码_用户](https://mmbiz.qpic.cn/mmbiz_jpg/TpAfliaLqyRL8K7ZJr9BAnMTawnaNRSK1w8Wfyhz1j6G12tKI5iaPWPH7x8w0z1EQQrzbwg7PT18qdG5EfKh5enw/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

关键是，**事先完全没通知社区**！

这就像你信任的朋友突然把你们的共同回忆打包卖给了陌生人，而且连招呼都不打一声。

开源社区的信任感瞬间崩塌，用户们纷纷表示："我们被背叛了！"

### 社区反击：24小时内的"复仇"

但开源社区的反应速度超乎想象。

**仅仅一天后**，社区就推出了全新的替代方案——**OpenList**。

这是基于AList最后一个安全版本fork出来的分支，开发者向所有用户郑重承诺：**永远开源，永远透明**。

结果呢？短短几个月时间，OpenList就暴涨了17000+ GitHub Star！

![Star History Oct 18 2025](https://mmbiz.qpic.cn/mmbiz_png/TpAfliaLqyRL8K7ZJr9BAnMTawnaNRSK1VgAEBf1pTwpXvkXJADXYHVibWXQaZz8CFKE6xBr3WK0XccVwWFibQq5g/640?wx_fmt=png&from=appmsg#imgIndex=1)

这增长速度，简直是开源界的"复仇爽文"现实版。

### OpenList到底有多强？一个界面统管30+网盘

OpenList继承了AList的所有核心功能，但做得更好。

**最核心的能力**：把各种云存储服务集中到一个界面里管理。

想象一下，以前你要在手机上切换N个App才能找到所有文件，现在只需要打开一个地方，所有云盘的内容一目了然。

支持的云存储服务多到让人惊讶：

- **国内主流**：阿里云盘、百度网盘、夸克网盘、迅雷云盘、115网盘
- **国外大厂**：OneDrive、Google Drive、Dropbox
- **企业级**：腾讯云COS、阿里云OSS等

![image-20251018111402554](https://mmbiz.qpic.cn/mmbiz_png/TpAfliaLqyRL8K7ZJr9BAnMTawnaNRSK1ic48ARY1Dg8fP04WFFAjkgrA1eW8lNXJvmZicNibVlwCLgfCIb5xtrbGA/640?wx_fmt=png&from=appmsg#imgIndex=2)

官方支持列表显示，总共支持**30多种存储服务**。

配置过程也很简单：进入后台管理页面，点"添加存储"，选择云盘类型，填写授权信息就搞定。

![640](https://mmbiz.qpic.cn/mmbiz_png/TpAfliaLqyRL8K7ZJr9BAnMTawnaNRSK1ma8X5EibFPnicetHCDAkAH0xMwicmnFNoGN8iabXs9Cv57ic3ttqyfDh3Ew/640?wx_fmt=png&from=appmsg#imgIndex=3)

### 在线预览功能：告别下载-打开-删除的循环

OpenList的在线预览功能特别实用，彻底解放了"下载强迫症"患者。

**视频音频**：直接在浏览器播放，还能加载字幕和歌词，体验堪比专业播放器。

**Office文档**：Word、Excel、PPT直接预览，不用装Office也能查看内容。

**代码文件**：语法高亮显示，程序员看代码再也不用下载到本地。

**图片浏览**：画廊模式查看，特别适合浏览大量照片，体验比原生云盘App还好。

![640](https://mmbiz.qpic.cn/mmbiz_png/TpAfliaLqyRL8K7ZJr9BAnMTawnaNRSK12EEsC25weYHBSwUhhx40RF9NYUzZcaBW2E4piaonSvH1MeTuqyNbbFg/640?wx_fmt=png&from=appmsg#imgIndex=4)

### 隐藏的强大功能

除了基础的文件管理，OpenList还有一些让人眼前一亮的高级功能：

**WebDAV支持**：把云盘转换成WebDAV协议，可以配合各种第三方应用使用。

**批量操作**：多个文件或整个文件夹打包下载，效率提升不是一点半点。

**离线下载**：直接把网络资源下载到指定云盘，省去本地中转的麻烦。

**权限控制**：设置密码保护和访问认证，重要文件夹加上安全锁。

### 上手指南：三步搞定部署

OpenList推荐使用Docker部署，即使是新手也能快速上手：

**第一步**：拉取镜像
```
docker pull openlistteam/openlist:latest
```

**第二步**：运行容器（映射好数据目录和端口）

**第三步**：浏览器访问 `http://你的IP:5244`，用默认账号登录

![dashboard](https://mmbiz.qpic.cn/mmbiz_png/TpAfliaLqyRL8K7ZJr9BAnMTawnaNRSK1OicPoHpVErjOq6skdvqQcWRM31OsgpeScD3ZLhY239jTicyFMpSkpLoA/640?wx_fmt=png&from=appmsg#imgIndex=5)

**从AList迁移的用户**更是福音：官方提供了专门的迁移工具，配置和数据可以直接导入，几乎零成本切换。

![640](https://mmbiz.qpic.cn/mmbiz_jpg/TpAfliaLqyRL8K7ZJr9BAnMTawnaNRSK1viaGTh1NLw4LIv2O0KTHyhgG9aV5eB2FDdUeXYKJ4u2Bef9QEWe2oBQ/640?wx_fmt=jpeg&from=appmsg#imgIndex=6)

### 写在最后：开源精神的胜利

这个故事最精彩的地方在于，它完美诠释了开源社区的力量。

当原作者选择"变现"时，社区用行动证明了什么叫"开源精神"——24小时内推出替代方案，几个月内获得17000+用户支持。

OpenList不仅继承了AList的所有优点，更重要的是，它代表了开源社区对透明、开放、用户至上理念的坚持。

对于正在被多个云盘"折磨"的朋友来说，OpenList确实是个值得尝试的解决方案。特别是有NAS或服务器的技术爱好者，这绝对是提升云存储使用体验的神器。

**GitHub项目地址**：https://github.com/OpenListTeam/OpenList

云盘管理的新时代已经到来，你准备好告别"云盘焦虑症"了吗？