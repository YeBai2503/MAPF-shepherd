# 多智能体路径规划————牧羊问题

## 一、 问题描述

建立羊与牧羊犬的行为模型，模拟牧羊犬将羊群驱赶至指定地点。

## 二、优化

### 1. 性能优化

* 向量化计算：使用基于Numpy的向量化计算提升部分代码计算性能。例如寻找r_a范围内的邻居等，这种需要对所有羊的位置进行处理的计算。

* 并行计算：使用多进程并行计算来加快采样统计模块程序的运行。

### 2. 模型优化

当牧羊犬前往目标位置需要穿过羊群时，移动方向改为牧羊犬与羊群质心连线的垂直方向（近似于羊群构成的圆的切线），垂直方向为靠近原移动方向一侧的垂直方向。

* 提升效果：主要提升表现在羊数量较大时，能有效减少放牧步数。50只羊时影响较小，100只羊时可减少约30%的平均步数（本模型中）。（详情可见 `result\100羊\改进前`和`result\100羊\改进后` 文件夹中的统计结果）
  
  > 原因可能有：羊数量较大时，羊群范围大，更容易产生牧羊犬需要穿过羊群的情况。

## 三、论文原模型可能忽略的因素

1. 计算排斥力时没有考虑到与排斥物体的距离远近的影响。(距离越近排斥力越大)
2. 牧羊犬的移动模型中没有考虑到牧羊犬的惯性因素

## 四、部分结果展示

* 静态轨迹图

![3](G:\code\project\MAPF_shepherd\results\50羊\原始参数结果\3.png)

* GIF动图

![1](G:\code\project\MAPF_shepherd\results\100羊\改进后\1.gif)

* 频率条形统计图

![Step_histogram](G:\code\project\MAPF_shepherd\results\50羊\原始参数结果\Step_histogram.png)

## 参考文献

[Solving the shepherding problem: heuristics for herding autonomous, interacting agents](https://royalsocietypublishing.org/doi/full/10.1098/rsif.2014.0719)
