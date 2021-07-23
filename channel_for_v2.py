"""
说明：此文件对应v2以上 APK 签名
签名工具：apksigner.jar （/Android/sdk/build-tools/30.0.3/lib/apksigner.jar）

打渠道包的原理：
1、首先用AndroidStudio打一个母包,可以采用AndroidStudio默认打包方式打母包。
// studio默认为v1v2签名
signingConfigs {
    config {
        storeFile file("android.keystore")
        storePassword "123456"
        keyAlias "android.keystore"
        keyPassword "123456"
    }
}
2、构建好V1签名的母包后，拷贝母包 并 重命名为对应渠道的apk名称；
3、将渠道信息写入到 apk中 META-INF 路径下；
4、使用工具apksigner.jar重新签名apk；
（/Android/sdk/build-tools/30.0.3/lib/apksigner.jar）

签名版本校验：
java -jar apksigner.jar verify -v xxx.apk
"""

import os
import shutil
import zipfile

# 输入文件夹
INPUT_FILE_DIR = 'input-V2V3/'
# 站内包 渠道文件
ZN_CHANNELS_TXT = INPUT_FILE_DIR + 'zn_channels.txt'
# 市场包 渠道文件
ZSC_CHANNELS_TXT = INPUT_FILE_DIR + 'zsc_channels.txt'
# 母包的名称为: test-release-V2.apk
MOTHER_APK = INPUT_FILE_DIR + 'test-release.apk'
# 打包apk的版本号
MOTHER_VERSION = 'v1.0.0'
# 要写入APK的渠道文件 暂时命名为 channel_null.txt
CHANNEL_EMPTY_FILE = INPUT_FILE_DIR + 'channel_null.txt'


# 这个方法用于构建渠道包。入口参数含义如下：
# channel_file 渠道文件名 zn_channels.txt 或 zsc_channels.txt
# mother_apk V2版本签名的母包，例：test-release.apk；
# mother_apk_version 母包的版本号；
def build_channel_apk(channel_file_txt, mother_apk, mother_apk_version, channel_empty_file):
    # 判空处理
    if not os.path.exists(channel_file_txt):
        print("channel_file_txt file does not exist ")
        return;
    if not os.path.exists(mother_apk):
        print("mother_apk file does not exist ")
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
    #
    # 母包apk：
    # 输入母包的apk名称 例：test-release.apk
    mother_apk_file_name = os.path.basename(mother_apk)
    mother_apk_name_split_list = os.path.splitext(mother_apk_file_name)
    # 若母包为 test-release.apk ，则此处为test-release
    mother_apk_name_pre = mother_apk_name_split_list[0]
    # .apk
    mother_apk_name_extension = mother_apk_name_split_list[1]
    #
    # 读取渠道文件的每一行数据：
    # 打开渠道文件 zn_channels.txt
    f = open(channel_file_txt)
    # 读取渠道文件 每一行的渠道数据
    channel_file_lines = f.readlines()
    f.close()
    #
    # 创建输出文件夹：output_ zn_channels _ test-release/
    output_dir = 'output_V2V3_' + channel_file_name_pre + '_' + mother_apk_name_pre + '/'
    # 如果输出文件夹存在，删除文件和文件夹；
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    # 重新创建输出文件夹
    os.mkdir(output_dir)
    # 循环 渠道文件的每一行数据
    for line in channel_file_lines:
        #
        # 1、拷贝：
        # 360
        target_channel = line.strip()
        # output_zn_channels_test-release/ test-release - 360 - v1.0.0 .apk
        channel_apk = output_dir + mother_apk_name_pre + "-" + target_channel + "-" + mother_apk_version + mother_apk_name_extension
        # 拷贝母包：将母包拷贝到target_apk路径下
        shutil.copy(mother_apk, channel_apk)
        #
        # 2、创建渠道文件，写入到压缩包中：
        # 压缩包：output_zn_channels_test-release/test-release-360-v1.0.0.apk
        zipped = zipfile.ZipFile(channel_apk, 'a', zipfile.ZIP_DEFLATED)
        # create META-INF/channel_360
        empty_channel_file = "META-INF/channel_{channel}".format(channel=target_channel)
        print(empty_channel_file)
        # 将指定文件 channel_empty_file 添加到zip文档中,
        # 添加到文档中后命名为 META-INF/channel_360_open
        zipped.write(channel_empty_file, empty_channel_file)
        zipped.close()
        #
        # 3、重新签名：
        print('start signing....')
        # output_zn_channels_test-release/ test-release - 360 - v1.0.0 .apk
        target_sign_apk = output_dir + mother_apk_name_pre + "-" + target_channel + "-" + mother_apk_version + "-v2v3" + mother_apk_name_extension
        # 签名证书配置信息
        # --ks [签名证书路径] output_zn_channels_test-release/android.keystore
        ks = 'android.keystore'
        # --ks-key-alias [别名] android.keystore
        ks_alias = 'android.keystore'
        # --ks-pass pass: [KeyStore密码] 123456
        ks_pass = '123456'
        # --key-pass pass: [签署者的密码] 123456
        key_pass = '123456'
        # --out [output.apk] [input.apk]
        output_apk = target_sign_apk
        input_apk = channel_apk
        # 拼接 签名 命令
        sign_cmd = "java -jar apksigner.jar sign --ks %s --ks-key-alias %s --ks-pass pass:%s --key-pass pass:%s --out %s %s" % (
            ks, ks_alias, ks_pass, key_pass, output_apk, input_apk)
        print(sign_cmd)
        # 执行命令，并打印日志信息
        tmp = os.popen(sign_cmd).readlines()
        print(tmp)
        #
        # 删除input_apk
        os.remove(input_apk)
    #
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
