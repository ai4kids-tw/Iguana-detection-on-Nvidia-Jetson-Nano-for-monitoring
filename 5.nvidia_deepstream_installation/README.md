# DeepStream for Jetson 設置教學
本教學示範將 Nvidia TLT 3.0 輸出的 .etlt 模型在 Jetson Nano 上進行佈署。以下為環境相關配置的訊息：
- TLT 3.0 模型訓練環境
    - Ubuntu 18.04
    - Cuda 11.2
    - TLT 3.0
    - TensorRT 7.2
    
- Jetson Nano 模型佈署環境
    - Jetpack 4.5
    - Cuda 10.2
    - TensorRT 7.1.3
    - Deepstream 5.1
    

## 下載 Jetpack
要使用最新版本的 Deepstream，需要下載最新版本的 Jetpack 然後燒錄成開機碟讓 Jetson Nano 使用。點選 [下載連結](https://developer.nvidia.com/embedded/jetpack) 下載最新版本的 Jetpack.

![](https://i.imgur.com/AJLhSYc.png)

## Jetpack 系統燒錄
下載 [etcher](https://www.balena.io/etcher/) 製做 Jetpack micro-sd 系統碟
![](https://i.imgur.com/fH7Qzya.png)

指定下載的 Jetpack zip，燒錄到 micro-sd 當中。 
![](https://i.imgur.com/jF8A2vm.png)
![](https://i.imgur.com/uKWYem0.png)
![](https://i.imgur.com/eDXojiO.png)




## 無線網卡驅動安裝 (Asus AC53) 
Asus AC53 是眾多 Jetson 系列可使用的 wifi-dongle 當中速度最快的，也是次專案當中使用的設備。但是，Asus AC53 並非隨插即用，來自 Nvidia developer forum 的[貼文](https://forums.developer.nvidia.com/t/building-driver-for-asus-usb-ac-53-nano-wi-fi-adapter/65415/8)的提供了有效的解決方案。
- Unplug wifi dongle - not sure if I need this but stay on safe side
- Clone: (git clone https://github.com/jeremyb31/rtl8822bu; cd rtl8822bu)
- Compile: ARCH=arm64 make -j4
- Install: sudo make install
- Reboot - not sure if I need this but stay on safe side
- Check if working: nmcli d wifi list
- Connect to wifi: sudo nmcli device wifi connect <MY_WIFI> password <MY_PASSWORD>
- Enjoy it

## Deepstream 環境安裝
### Deepstream 環境快速設置流程
-官方提供之快速設置呈請參閱此[連結](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Quickstart.html)
![](https://i.imgur.com/mIY7CMT.png)

### 1.安裝相依套件
![](https://i.imgur.com/EuPIoSW.png)

指令：
> sudo apt install \
> libssl1.0.0 \
> libgstreamer1.0-0 \
> gstreamer1.0-tools \
> gstreamer1.0-plugins-good \
> gstreamer1.0-plugins-bad \
> gstreamer1.0-plugins-ugly \
> gstreamer1.0-libav \
> libgstrtspserver-1.0-0 \
> libjansson4=2.11-1
> 
### 2.安裝 Kafka
![](https://i.imgur.com/LQT1X6K.png)

指令：
> git clone https://github.com/edenhill/librdkafka.git
> cd librdkafka
> git reset --hard 7101c2310341ab3f4675fc565f64f0967e135a6a
> ./configure
> make
> sudo make install

### 3.下載與安裝 Deepstream
- Deepstream 的[官方下載連結](https://developer.nvidia.com/deepstream-getting-started)。
- 選擇 DeepStream 5.1 for Jetson 的 Download .deb
![](https://i.imgur.com/VbLEunq.png)

安裝指令：
> sudo dpkg -i <deepstream檔案名稱>.deb




## Deepstream 應用測試 [1 hour]
Deepstream 安裝完畢以後，可以使用自帶的範例程式碼來做功能測試，確定安裝正常。以下測試物件偵測與追蹤的範例程式是否可以順利運行。

測試指令：
> cd /opt/nvidia/deepstream/deepstream-5.1/samples/configs/deepstream-app
> deepstream-app -c source4_1080p_dec_infer-resnet_tracker_sgie_tiled_display_int8.txt

##### 若順利運行，則結果應如下圖
![順利運行之結果](https://i.imgur.com/047RI2E.jpg)



## TLT to DeepStream workflow [2 hours]
### .etlt 預訓練模型轉換
根據本文表示，將 TLT 訓練完的 .etlt 模型編譯成 TensorRT 引擎，需要透過 tlt-converter 轉換，並且轉換過程不能跨平台。

要想將 TLT 訓練出來的模型佈署到 Jetson 系列，只能使用 Jetson 專屬的 tlt-converter 完成，不能使用其他平台的 tlt-converter。 

要想將 TLT 訓練完的模型佈署到 Jetson 上面，需要：
- 下載 Jetson 專屬 tlt-converter
- 將 tlt-converter 放進 Jetson 設備當中
- 使用 Jetson 進行模型轉換
- TLT 訓練完的模型，可以透過 TensorRT 匯出成 fp32 / fp16 / int8，但是 Jetson Nano  以及 Tx 系列只有 fp16 以上的選項，而不能轉換為 int8。


### 下載與安裝 tlt-converter
TensorRT 不同版本無法兼容，並且 Jetson 系列[無法任意更改、升級 TensorRT](https://forums.developer.nvidia.com/t/update-tensorrt-to-7-2-in-jetson-nano/158524)。因此要能讓 TLT 與佈署於 Jetson 系列的 DeepStream 能夠運作必須下載正確的 tlt-converter 將 TLT 預訓練模型轉換為 Jetson 系列符合的 TensorRT 版本。以下為官方所提供的 tlt-converter 組合，開發者應該注意對應上自己的開發環境。

| Platform | Compute  |
| -------- | -------- |
| x86 + GPU    | CUDA 10.2 / cuDNN 8.0 / TensorRT 7.1     |
| x86 + GPU     | CUDA 10.2 / cuDNN 8.0 / TensorRT 7.2     |
| x86 + GPU     | CUDA 11.0 / cuDNN 8.0 / TensorRT 7.1     |
| x86 + GPU     | CUDA 11.0 / cuDNN 8.0 / TensorRT 7.2     |
| x86 + GPU     | CUDA 11.1 / cuDNN 8.0 / TensorRT 7.2     |
| x86 + GPU     | CUDA 11.2 / cuDNN 8.1 / TensorRT 7.2     |
| Jetson     | Jetpack 4.4    |
| Jetson     | Jetpack 4.5    |


### 1. 使用 tlt-converter 轉換模型
Nvidia 官方提供了用來轉換到不同環境配置的 tlt-converter，點此[連結](https://developer.nvidia.com/tlt-get-started)針對要佈署的環境下載對應的 tlt-converter，在此案例當中佈署的對象是 Jetson Nano，因此選擇 Jetson + Jetpack 4.5 的選項下載。請將此 tlt-converter 放到適合的資料夾當中，未來每次 TLT 到 Jetson 的流程都會使用這一份。
#### 下載區塊
![](https://i.imgur.com/7P4BcYQ.png)
#### 解壓縮後之資料夾結構
![](https://i.imgur.com/TnPSWyl.png)
#### 按照 Readme.txt 進行安裝與設定
![](https://i.imgur.com/mN1a3uq.png)
指令：
> sudo apt-get install libssl-dev
> export TRT_LIB_PATH=”/usr/lib/aarch64-linux-gnu”
> export TRT_INC_PATH=”/usr/include/aarch64-linux-gnu”
> cd <你下載的 tlt-converter 資料夾位置>
> chmod +x tlt-converter

到這裡，tlt-converter 已經被正確設定。

#### 升級 OSS 插件
Deepstream 對於一些 TLT 當中新的模型，其 OSS 插件不能支援的(例如：yolo)，透過升級此插件才能夠執行的模型。設定方法請見此[連結](https://github.com/NVIDIA-AI-IOT/deepstream_tlt_apps)。
##### Github repo 首頁
![](https://i.imgur.com/VvXSETf.png)
##### 需要升級 OSS 才能使用的模型

- SSD
- DSSD
- RetinaNet
- YoloV3
- YoloV4
- PeopleSegNet

##### 建立 OSS 插件
此連結內含詳細[編譯插件](https://github.com/NVIDIA-AI-IOT/deepstream_tlt_apps/tree/master/TRT-OSS/Jetson/TRT7.1)步驟，適合 Jetpack 4.5 環境。
![](https://i.imgur.com/OZfCHiW.png)
![](https://i.imgur.com/wi7UbxP.png)

安裝 Cmake 3.19.4 指令：
> sudo dpkg --force-all -r cmake
> wget https://github.com/Kitware/CMake/releases/download/v3.19.4/cmake-3.19.4.tar.gz
> tar xvf cmake-3.19.4.tar.gz
> cd cmake-3.19.4/
> ./configure
> make -j$(nproc)
> sudo make install
> sudo ln -s /usr/local/bin/cmake /usr/bin/cmake

創建 TensorRT Oss 插件指令：
> git clone -b release/7.1 https://github.com/nvidia/TensorRT
> cd TensorRT/
> git submodule update --init --recursive
> export TRT_SOURCE=`pwd`
> cd TRT_SOURCE
> mkdir -p build && cd build
> /usr/local/bin/cmake .. -DGPU_ARCHS="53 62 72" -DTRT_LIB_DIR=/usr/lib/aarch64-linux-gnu/ -DCMAKE_C_COMPILER=/usr/bin/gcc -DTRT_BIN_DIR=`pwd`/out
> make nvinfer_plugin -j$(nproc)

TensorRT Oss 插件替換指令：
> sudo mv /usr/lib/aarch64-linux-gnu/libnvinfer_plugin.so.7.x.y ${HOME}/libnvinfer_plugin.so.7.x.y.bak   // backup original libnvinfer_plugin.so.x.y
> sudo cp `pwd`/out/libnvinfer_plugin.so.7.m.n  /usr/lib/aarch64-linux-gnu/libnvinfer_plugin.so.7.x.y
> sudo ldconfig

## .etlt 預訓練模型轉換
![](https://i.imgur.com/gE6D2Gj.png)

以我預訓練的 yolo_v4 模型為例，使用此前下載的 tlt-converter 最終順利的轉換成 TensorRT 引擎。
- ./tlt-converter -k nvidia_tlt -d 3,384,1248 -o BatchedNMS -e ./trt.fp16.engine -t fp16 -i nchw -m 1 ./yolov4_cspdarknet53_fp16_epoch_080.etlt


### 其他參考
- ./tlt-converter -k nvidia_tlt -d 3,384,1248 -o BatchedNMS -e ./trt.fp16.engine -t fp16 -i nchw -m 1 ./yolov4_cspdarknet53_fp16_epoch_080.etlt

- tlt-converter 使用[參考](https://docs.nvidia.com/metropolis/TLT/tlt-user-guide/text/object_detection/yolo_v4.html)
- DeepStream 使用 TLT 預訓練模型的文件配置範例請看此[ Github repo](https://github.com/NVIDIA-AI-IOT/tlt-iva-examples/tree/master/deepstream)
- 部份 TLT 模型的種類較新(如 yolo 系列)，如果需要在 DeepStream 當中使用這些新的模型則需要進行插件更新，請看此[Github repo](https://github.com/NVIDIA-AI-IOT/deepstream_tlt_apps).
- 乘上則，编译 TensorRT OSS 插件出现问题：The CUDA compiler identification is unknown, 參考此解決方案，在命令列當中多加入 CUDA 的選項即可 [解決方案]
- TLT 預訓練模型要佈署在 Jetson 系列設備之前，需要先轉換為 TensorRT engine，因此需要視該裝備上的 環境配置選擇正確的轉換方式。
- TensorRT 不同版本無法兼容，並且 Jetson 系列[無法任意更改、升級 TensorRT](https://forums.developer.nvidia.com/t/update-tensorrt-to-7-2-in-jetson-nano/158524)。因此要能讓 TLT 與佈署於 Jetson 系列的 DeepStream 能夠運作必須符合其中下列任一個條件： 
    - TLT 的環境(Cuda / TensorRT)版本必須與 Jetson 系列相符
    - 使用正確的 tlt-converter 將 TLT 預訓練模型轉換為 Jetson 系列符合的 TensorRT 版本，不同版本的 tlt-converter 可在此[下載](https://developer.nvidia.com/tlt-get-started) tlt-converter 的各種選項。


- (https://blog.csdn.net/weixin_41783910/article/details/108547344).

### 效率指標參考
TLT 預訓練模型的運行效率指標，參考此[連結](https://docs.nvidia.com/metropolis/deepstream/5.0/dev-guide/index.html#page/DeepStream_Development_Guide/deepstream_performance.html)。
### Deepstream & SSD
https://forums.developer.nvidia.com/t/creating-engine-file-of-ssd-mobilenet-v2-to-run-on-deepstream-app/83109

https://elinux.org/Jetson/L4T/TRT_Customized_Example

SSD 的 deepstream-app 可以從以下路徑找到範例檔案：/opt/nvidia/deepstream/deepstream-5.1/sources/objectDetector_SSD/nvdsinfer_custom_impl_ssd

SSD slow fps issue:
https://forums.developer.nvidia.com/t/slow-fps-using-ssd-mobilenetv2/107618/4

Deepstream 原理解說：
http://stevegigijoe.blogspot.com/2020/03/


