"""
说明：此文件只对应v1版本 APK 签名

前提条件：
1、母包APK 为v1签名APK
2、检查签名是否成功：(Android/sdk/build-tools/28.0.3/lib/apksigner.jar)
java -jar apksigner.jar verify -v xxx.apk

打渠道包的原理：
1、首先用AndroidStudio打一个母包，这个母亲包必须是V1签名的；
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
2、构建好V1签名的母包后，拷贝母包 并 重命名为对应渠道的apk名称；
3、将渠道信息写入到 apk中 META-INF 路径下；
4、Android 工程中，从 META-INF 中读取渠道信息：
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
"""

import os
import shutil
import zipfile

# 输入文件夹
INPUT_FILE_DIR = 'input-V1/'
# 站内包 渠道文件
ZN_CHANNELS_TXT = INPUT_FILE_DIR + 'zn_channels.txt'
# 市场包 渠道文件
ZSC_CHANNELS_TXT = INPUT_FILE_DIR + 'zsc_channels.txt'
# 母包的名称为: test-release.apk
MOTHER_APK = INPUT_FILE_DIR + 'test-release.apk'
# 打包apk的版本号
MOTHER_VERSION = 'v1.0.0'
# 要写入APK的渠道文件 暂时命名为 channel_null.txt
CHANNEL_EMPTY_FILE = INPUT_FILE_DIR + 'channel_null.txt'


# 这个方法用于构建渠道包。入口参数含义如下：
# channel_file 渠道文件名 zn_channels.txt 或 zsc_channels.txt
# mother_signed_apk V1版本签名的母包，例：test-release.apk；
# mother_apk_version 母包的版本号；
def build_channel_apk(channel_file_txt, mother_signed_apk, mother_apk_version, channel_empty_file):
    # 判空处理
    if not os.path.exists(channel_file_txt):
        print("channel_file_txt file does not exist ")
        return;
    if not os.path.exists(mother_signed_apk):
        print("mother_signed_apk file does not exist ")
        return;
    #
    # 初始化要写入的渠道文件：
    # 如果存在该文件，先删除
    if os.path.exists(channel_empty_file):
        os.remove(channel_empty_file)
    # 创建要写入的渠道文件
    f = open(channel_empty_file, 'w')
    f.close()
    #
    # 渠道包：
    # 渠道文件名称 例：zn_channels.txt 或 zsc_channels.txt
    channel_file_name = os.path.basename(channel_file_txt)
    channel_file_name_split_list = os.path.splitext(channel_file_name)
    # 若渠道包为 zn_channels.txt ，则此处为 zn_channels
    channel_file_name_pre = channel_file_name_split_list[0]

    # 母包apk：
    # 输入母包的apk名称 例：test-release.apk
    mother_apk_file_name = os.path.basename(mother_signed_apk)
    mother_apk_name_split_list = os.path.splitext(mother_apk_file_name)
    # 若母包为 test-release.apk ，则此处为test-release
    mother_apk_name_pre = mother_apk_name_split_list[0]
    # .apk
    mother_apk_name_extension = mother_apk_name_split_list[1]

    # 读取渠道文件的每一行数据：
    # 打开渠道文件 zn_channels.txt
    f = open(channel_file_txt)
    # 读取渠道文件 每一行的渠道数据
    channel_file_lines = f.readlines()
    f.close()

    # 创建输出文件夹：output_ zn_channels _ test-release/
    output_dir = 'output_V1_' + channel_file_name_pre + '_' + mother_apk_name_pre + '/'
    # 如果输出文件夹存在，删除文件和文件夹；
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    # 重新创建输出文件夹
    os.mkdir(output_dir)
    # 循环 渠道文件的每一行数据
    for line in channel_file_lines:
        # 360
        target_channel = line.strip()
        # output_zn_channels_test-release/test-release-360-v1.0.0.apk
        target_apk = output_dir + mother_apk_name_pre + "-" + target_channel + "-" + mother_apk_version + "-v1" + mother_apk_name_extension
        # 拷贝母包：将母包拷贝到target_apk路径下
        shutil.copy(mother_signed_apk, target_apk)
        # 解压：output_zn_channels_test-release/test-release-360-v1.0.0.apk
        zipped = zipfile.ZipFile(target_apk, 'a', zipfile.ZIP_DEFLATED)
        # create META-INF/channel_360
        empty_channel_file = "META-INF/channel_{channel}".format(channel=target_channel)
        print(empty_channel_file)
        # 将指定文件 channel_empty_file 添加到zip文档中,
        # 添加到文档中后命名为 META-INF/channel_360_open
        zipped.write(channel_empty_file, empty_channel_file)
        zipped.close()

    # output_ zn_channels_ test-release/ test-release -goole_market_open .apk
    google_apk = output_dir + mother_apk_name_pre + "-goole_market_open" + mother_apk_name_extension
    # output_ zn_channels_ test-release/ test-release -goole_market_open_zipaligned .apk
    google_apk_zipaligned = output_dir + mother_apk_name_pre + "-goole_market_open_zipaligned" + mother_apk_name_extension
    # exists
    if os.path.exists(google_apk):
        tmp = os.popen('zipalign -f 4 ' + google_apk + " " + google_apk_zipaligned).readlines()
        print(tmp)


# 构建渠道包
# 构建站内渠道包
build_channel_apk(ZN_CHANNELS_TXT, MOTHER_APK, MOTHER_VERSION, CHANNEL_EMPTY_FILE)
# 构建应用市场渠道包
build_channel_apk(ZSC_CHANNELS_TXT, MOTHER_APK, MOTHER_VERSION, CHANNEL_EMPTY_FILE)
