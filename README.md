# Iguana detection on Nvidia Jetson Nano for monitoring

![](https://i.imgur.com/c8iOqsX.jpg)


## 目錄
* 專案大綱
* 專案動機
* 資料蒐集
    * 圖片爬蟲
    * 圖片標籤
    * 標籤格式
* Nvidia TLT
    * 簡介與安裝
    * 模型訓練、優化
* 佈署模型於 Jetson 裝置
    * Deepstream 簡介與安裝
    * 推論結果即時串流
* 數據儀表板
    * Plotly Dash 

## 1. 專案大綱
本頁面是 Nvidia Jetson 社群中的公益開源專案「綠鬣蜥個體偵測與監控」的 Github repo，使用 Jetson Nano 搭配電腦視覺之物件偵測模型即時偵測綠鬣蜥的行蹤與呈現。我們將展示此專案的流程，讓使用者能夠依照此 repo 進行類似專案的模式複製與開發。

## 2. 專案動機

### 2-1. 什麼是綠鬣蜥？
美洲鬣蜥又名綠鬣蜥，是一種生活在樹上的大型蜥蜴，頭尾全長可達1～2公尺，壽命可長達10年以上，以植物的葉、嫩芽、花、果實為食物，為日行性爬蟲類，每胎可產24-45顆卵，繁殖力、環境適應能力極強。

### 2-2. 綠鬣蜥帶來之生態浩劫嚴重性
在台灣，棄養的綠鬣蜥在快速野外繁殖，本國農委會林務局曾表示，綠鬣蜥問題不不僅危害生態，其攝食植物造成農民的農作物損失、並且由於綠鬣蜥有挖洞之習慣，常在河堤、魚塭旁挖洞，破壞設施。以政府目前監控下所知，綠鬣蜥的行蹤已擴散多個縣市。

### 2-3. 建立綠鬣蜥監控系統
得力於近年來 Edge device 的發展，我們得以開發、佈署實時電腦視覺應用，藉以偵測、監控綠鬣蜥的行蹤，通過系統即時告警與通報，能採取措施避免綠鬣蜥帶來的資產損失問題。


## 3. 資料蒐集
![綠鬣蜥圖片標籤範例](https://i.imgur.com/98T5ZmX.jpg)
### 3-1. 圖片爬蟲
透過 selenium 動態網路爬蟲，我們蒐集了5000張左右的綠鬣蜥圖片，並一一進行標籤。在此我們也開放圖片、標籤資料的下載，請見此[連結](https://drive.google.com/drive/u/2/folders/1oeFxH4JQ7JJeSNpt521quuHZjugVbZlz)。
### 3-2. 圖片標籤
在多人標籤的作業當中，我們使用了網頁版的物件偵測標籤工具 makesense.ai 來進行，因為其簡單易用的特性，也因為無須另行安裝單機版本的標籤工具。使用此工具的教學文檔見此[連結](https://hackmd.io/iq1tHBp8SfS6hAnj0ZKIEA)。

### 4. Nvidia TLT 訓練綠鬣蜥偵測模型
![](https://i.imgur.com/pNMocSI.png)

從頭開始創建 AI/ML 模型來解決業務問題是一項成本極高的過程，因此通常專案開發時會使用「遷移學習」來加速開發。遷移學習是屬於機器學習的一種研究領域，它專注於存儲已有問題的解決模型，例如使用預訓練的模型，將其利用在其他不同但相關問題上。

NVIDIA 所提供的 TLT (Transfer Learning Toolkit) 顧名思義就是遷移學習的工具包，提供了圖像、自然語言處理的熱門預訓練模型做遷移學習。TLT 最重要的是面向佈署的目的；針對模型訓練完畢後的尺寸縮減、優化都被整合在 TLT 的功能當中。

在最理想的情況下使用 TLT 做模型的訓練僅需要設定訓練參數；不用從頭撰寫程式碼。TLT 實現了訓練、優化、佈署的端到端流程，這與一般的開發流程有極大的不同，大大減少了專案開發的時間、技術成本。

#### 4-1. 硬體需求
官方所建議的運行 Nvidia TLT 的硬體配置:
* 32 GB system RAM
* 32 GB of GPU RAM
* 8 core CPU
* 1 NVIDIA GPU
* 100 GB of SSD space

#### 4-2. 軟體需求
***要運行 NVIDIA TLT 必須滿足以下所有軟體的安裝需求，缺一不可：***
| Software | Version  |
| -------- | -------- |
| Ubuntu 18.04 LTS    | 18.04     |
| python     | >=3.6.9     |
| docker-ce     | >19.03.5     |
| docker-API     | 1.40     |
| nvidia-container-toolkit     | >1.3.0-1     |
| nvidia-container-runtime     | 3.4.0-1     |
| nvidia-docker2     | 2.5.0-1     |
| nvidia-driver     | >455     |
| python-pip     | >21.06     |
| nvidia-pyindex     |      |


#### 4-3. NVIDIA TLT 安裝教學
在此我們提供了一份詳細的 NVIDIA TLT 安裝教學，請見此連結。

#### 4-4. 模型訓練、優化
此專案的物件偵測模型為 yolo v4，我們使用 TLT 當中檢附的 yolo v4 模型訓練範例程式碼稍作修改後，便能使用綠鬣蜥的圖片、標籤來訓練模型。

運行 tlt_training/yolo_v4_iguana_detection.ipynb 中的程式碼，等待程式全部執行完畢後，會自動匯出一 .etlt 檔案，便是我們最終要佈署的模型檔案。

TLT 其他的 CV 使用範例程式碼皆可在此[連結](https://ngc.nvidia.com/catalog/resources/nvidia:tlt_cv_samples/quickStartGuide)內找到，幾乎都是只要稍微調整參數即可一鍵訓練、優化、匯出。



## 5. 佈署模型於 Jetson 裝置
模型訓練完畢後，下一步是佈署於 Jetson 裝置進行即時推論，同時也需要將影像與推論結果進行串流。我們使用的是 Nvidia Deepstream，一個專為推論、資料串流而生的框架。

### 5-1. Deepstream 簡介
![](https://i.imgur.com/FGooTYu.png)

DeepStream 執行階段系統是一套端對端的流程，可以進行深度學習推論、影像和感測器處理，並在串流應用程式中將洞見傳送至雲端。您可以使用容器建構雲端原生的 DeepStream 應用程式，並透過 Kubernetes 平台執行協調，以進行大規模的部署。當部署在邊緣端時，應用程式可以在 IoT 裝置與雲端標準訊息代理程式（例如 Kafka 和 MQTT）之間通訊，以進行大規模的廣域部署。

### 5-2. TensorRT 簡介
NVIDIA TensorRT™是用於深度學習推理的SDK。SDK包含深度學習學習優化器運行時環境，使深度學習學習應用提供低延遲和高吞吞。在進行模型佈署之前，需要 TensorRT 對模型進行轉換，加快推論時的運行速度。

TLT 是以佈署目的為導向的模型訓練框架，自然包含了針對訓練後模型的轉換功能。只要使用 tlt-converter 就可以對 TLT 訓練完畢的 .etlt 輸出模型進行 TensorRT 的推論引擎建置。另外，針對裝置佈署的硬體、軟體都需要用相應的  tlt-converter 版本進行轉換。以下為所有配置的選項：

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

### 5-3. Deepstream 環境安裝
透過此連結，我們記錄了 Deepstream 環境安裝的步驟，以及 .etlt 模型的 TensorRT 引擎建置過程。其中也包含安裝此專案所需要的其他套件的方法，如 MQTT client…等等。

### 5-4. Deepstream 運行
deepstream_app/deepstream_mqtt_rtsp_out.py 是 deepsteam python binding 的運行配置。此程式在進行物件偵測推論時，會將圖片以 RTSP 的方式進行串流，並且將推論結果之數據傳送到 MQTT broker、儲存至資料庫以方便之後的視覺化。

## 6. 數據儀表板
### 6-1. Plotly Dash
Plotly Dash 是一個資料可互動式視覺化的框架，可以用非前端的語言來撰寫一個資料視覺化的前端頁面，同時本套件延伸的其他子套件更是將網頁風格與排版的過程極簡化，非常適合快速開發基於網頁的資料視覺化。

另外，該套件提供的 live-update 功能，可以讓網頁持續動態更新，特別適合本專案的儀表板需求。
![](https://i.imgur.com/rVhFy6B.png)
### 6-2. Dash Bootstrap Components
![](https://i.imgur.com/0RwVQkY.png)

Bootstrap是一組用於網站和網路應用程式開發的開源前端框架，包括HTML、CSS及JavaScript的框架，提供字體排印、表單、按鈕、導航及其他各種元件及Javascript擴充套件，旨在使動態網頁和Web應用的開發更加容易。 

使用 Dash Bootstrap Components 可直接承襲 bootstrap 所定義好的框架，快速鍵置網頁的版面配置。 


### 6-3. MQTT broker
![](https://i.imgur.com/iMp3pno.png)


使用者可依照自己的喜好選用 MQTT broker，在此專案當中我們所使用的是 Eclipse Mosquitto。安裝好後只要啟動 MQTT broker 就能開始接收接收資料。

### 6-4. 資料庫建置
![](https://i.imgur.com/NmZAi0C.png)

本專案使用 mySQL 建置資料庫，使用者可挑選偏好的資料庫種類。資料庫的建目的是從 Jetson Nano 推論時發送至 MQTT broker 的資料流可以被寫入資料庫，透過 Plotly Dash 定時更新資料並且將最新的資料呈現於儀表板。

### 6-4. MQTT 主題訂閱並與數據寫入資料庫
Deepstream 在 Jetson Nano 上運行時通過 MQTT 通訊協定不斷向 MQTT broker 的特定主題發送推論結果之數據。透過設定此特定主題的訂閱者，就能在某主題有最新數據流入時收到通知、將數據寫入資料庫。此程式位置為 mqtt_topic_subscribe/mqtt_msg_to_db.py。


### 6-5. 運行網頁儀表板
- Deepstream 佈署與運行
- MQTT broker 運行於 data server
- Database 運行於 data server

具備以上的條件，網頁儀表板便可以開始運行了。請注意 Deepstream 的配置是可變動的，因此未來使用者若要將模型代換成其他物件偵測模型只要修改 Deepstream 的配置文件與 Deepstram python 執行檔案便可以。
