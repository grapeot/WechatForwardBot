## 斗图功能

目前对这个功能并没有官方支持。
这个文档只是为感兴趣的读者做一个参考。
要想部署使用这个系统，需要一些深度学习的知识和经验，并且需要读一下代码。

系统的基本框架是，用Caffe把所有图片的feature抽出来，构成一个数据库。
新的图片进来以后，抽feature，在这个数据库里面进行检索。
最接近的几个图里面随机挑选一个返回。

### 训练

* 安装Caffe。`installCaffe.sh`可以作为一个参考。几个要点：不要忘了`make pycaffe`；用OpenBLAS启用多线程可以减小Latency；如果有GPU的话可以大幅加速。
* 执行`dedupAndCopy.sh`转换文件格式。
* 执行`incrementalExtractFeatures.sh`抽取feature。
* 把生成的feature文件`featuresall.txt`拷贝到父目录，并且在main.py里面指定`DoutuProcessor`的文件路径。
