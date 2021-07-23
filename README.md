# ForAndroidChannelPackage

python3 实现Android 渠道包 APK 签名打包。

+ 签名版本
+ python环境
+ 渠道打包签名原理



## 一、签名版本
渠道包APK签名打包时 支持V1、V2、V3 签名

## 二、python环境
python环境：`python 3.8`
编译器：`PyCharm`

## 三、渠道打包原理

+ V1 版本渠道包；
+ V2、V3版本渠道包；

### 1.1 V1 版本渠道包

前提条件：**母包APK 为v1签名APK**

打渠道包的原理：

+ 1、首先用AndroidStudio打一个母包，这个母亲包必须是V1签名的；
使用Android Studio打包时，配置如下：
```
// studio默认为v1v2签名
signingConfigs {
    config {
        storeFile file("android.keystore")
        storePassword "123456"
        keyAlias "android.keystore"
        keyPassword "123456"
        // 采用V1签名
        v2SigningEnabled false
        // v1SigningEnabled false
    }
}
```

+ 2、构建好V1签名的母包后，拷贝母包 并 重命名为对应渠道的apk名称；
+ 3、将渠道信息写入到 apk中 META-INF 路径下；
+ 4、Android 工程中，从 META-INF 中读取渠道信息：

```
// 从 META-INF 中读取写入的渠道信息
private static String getChannelFromApk(Context context) {
    ApplicationInfo appinfo = context.getApplicationInfo();
    String sourceDir = appinfo.sourceDir;
    Log.d(TAG, "souceDir---" + sourceDir);
    String ret = "";
    ZipFile zipfile = null;
    try {
        zipfile = new ZipFile(sourceDir);
        Enumeration<?> entries = zipfile.entries();
        while (entries.hasMoreElements()) {
            ZipEntry entry = ((ZipEntry) entries.nextElement());
            String entryName = entry.getName();
            if (entryName.startsWith("META-INF") && entryName.contains("channel_")) {
                ret = entryName;
                break;
            }
        }
    } catch (IOException e) {
        e.printStackTrace();
    } finally {
        if (zipfile != null) {
            try {
                zipfile.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    String[] split = ret.split("_");
    String channel = "";
    if (split != null && split.length >= 2) {
        channel = ret.substring(split[0].length() + 1);
    }
    Log.d(TAG, "channel---"+channel);
    return channel;
}
```



### 1.2 V2 V3版本渠道包

+ 1、首先用AndroidStudio打一个母包,可以采用AndroidStudio默认打包方式打母包。

```
// studio默认为v2以上版本签名
signingConfigs {
    config {
        storeFile file("android.keystore")
        storePassword "123456"
        keyAlias "android.keystore"
        keyPassword "123456"
    }
}
```

+ 2、构建好母包后，拷贝母包 并 重命名为对应渠道的apk名称；
+ 3、将渠道信息写入到 apk中 META-INF 路径下；
+ 4、使用工具apksigner.jar重新签名apk；
工具路径：/Android/sdk/build-tools/30.0.3/lib/apksigner.jar



