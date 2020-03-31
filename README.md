# 基于PDFMiner的英文学术论文语义分割
+ [标注工具] (https://bhpan.buaa.edu.cn:443/link/92598A40D3D902B217C407A3CF8C636C)

![Image text](https://img.shields.io/badge/Version-v1.0.0-lightgrey)
+ [需求文档](https://github.com/Noba1anc3/Academic-Paper-PDF-SemSeg/wiki/%E5%AD%A6%E6%9C%AF%E8%AE%BA%E6%96%87%E8%AF%AD%E4%B9%89%E5%88%86%E5%89%B2---%E9%9C%80%E6%B1%82%E6%96%87%E6%A1%A3---v1.0)
+ [设计文档](https://github.com/Noba1anc3/Academic-Paper-PDF-SemSeg/wiki/%E5%AD%A6%E6%9C%AF%E8%AE%BA%E6%96%87%E8%AF%AD%E4%B9%89%E5%88%86%E5%89%B2---%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3---v1.0)

## 下载
#####   为下载该项目, 请在希望保存该项目的路径启动控制台并执行如下命令:
```
git clone https://github.com/Noba1anc3/Academic-Paper-PDF-SemSeg.git
```

## 环境
![Image text](https://img.shields.io/badge/Python-3.6-green?style=flat)
#####   项目运行所需要的依赖包如下所示：
 - pdfminer
 - numpy
 - logzero
 - opencv-python
 - pdf2image>=1.11.0
 
#####   可以逐一安装上述环境, 也可以在进入到`pdf_analysis`之内后执行如下命令: 
```
pip install -r requirements.txt
```

## 配置
本项目支持通过配置的方式启动，配置文件为`conf.cfg`, 可配置的功能如下：
 - `folder`: 默认设置为./example/pdf_file/, 其值为待处理的pdf文件所在目录.
 - `filename`: 默认设置为all, 表示对folder目录下的所有文件做语义分割. 若指定文件则请设置为文件名称.
 - `evaluate`: 默认设置为False, 表示不对语义分割结果做评估. 若对语义分割结果做评估则请设置为True.
 - `text_level`: 默认设置为2, 表示对文字区域做二级语义分割. 若对文字区域做一级语义分割则设为1.
 - `table_level`: 默认设置为2, 表示对表格区域做表格检测和单元格分割. 若只对表格区域做表格区域检测则请设置为1.
 - `tit_choice`: 默认设置为0, 表示对文字、图片和表格均做语义分割. 若只对文字区域做语义分割则请设置为1, 只对图片区域做语义分割则请设置为2, 只对表格区域做语义分割请设置为3. 
 - `save_image`: 默认设置为True, 表示保存语义分割结果的图片. 若不希望保存语义分割结果的图片, 请设置为False.
 - `save_text`: 默认设置为False, 表示不保存语义分析结果的JSON文件. 若希望保存语义分割结果的JSON文件, 请设置为True.

## 运行
```python
python main.py
```

## 测试
测试时，请在根目录下创建`example`文件夹, 并把pdf所在文件夹`pdf_file`和标注文件所在文件夹`annotation`分别放到`example`文件夹下, 在配置文件内启动测试功能后即可进行测试.
+ [PDF文件下载] (https://bhpan.buaa.edu.cn:443/link/92598A40D3D902B217C407A3CF8C636C)
+ [标注文件下载] ( https://bhpan.buaa.edu.cn:443/link/1D7D70A6EBA2284AD633C7F0BA1A6B37)

### 数据集
对AAAI、NeurlPS、ACL、CVPR、ICCV、ICML、IJCAI这七个学术会议，每种随机选取５篇论文，共35篇论文。

拥有每种语义类型的文档数目如下所示

| 标题 | 作者 | 注释 | 页码 | 图注 | 表注 | 图片 | 表格 | 单元格 |
| -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
| 35     | 35     | 27     | 20     | 34     | 33     | 34     | 33     | 33     |

每种语义类型的总个数如下所示

| 标题 | 作者 | 注释 | 页码 | 图注 | 表注 | 图片 | 表格 | 单元格 |
| -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
| 35     | 35     |  59    |  181   |   143    | 106     | 143     | 123     | 5574     |

### 测试结果

在标题、页码和单元格的IoU为0.5,图片和表格的IoU为0.8,其他区域的IoU为0.7时，预测正确的每种语义类型个数如下所示

| 标题 | 作者 | 注释 | 页码 | 图注 | 表注 | 图片 | 表格 | 单元格 |
| -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
| 35     | 34     |  58    |  180   |   139    | 106     | 126     | 107     | 5026     |

每种语义类型的相关测试结果如下所示

|| 基于个数的准确率 | 基于个数的召回率 | 基于个数的F1 | 基于面积的准确率 | 基于面积的召回率 | 基于面积的F1 |
| -------- | -------- | -------- | -------- | -------- | -------- | -------- |
|标题|100.0%|100.0%|1.00|100.0%|100.0%|1.00|
|作者|97.14%|97.14%|0.97|97.14%|97.14%|0.97|
|图注|96.47%|97.06%|0.97|96.72%|96.51%|0.97|
|表注|100.0%|98.48%|0.99|100.0%|98.27%|0.99|
|注释|74.07%|73.15%|0.74|74.07%|73.41%|0.74|
|页码|100.0%|100.0%|1.00|100.0%|100.0%|1.00|
|图片|84.74%|85.19%|0.85|88.64%|84.61%|0.86|
|表格|90.24%|95.96%|0.92|93.75%|95.93%|0.95|
|单元格|90.48%|95.07%|0.93|87.75%|89.03%|0.88|
