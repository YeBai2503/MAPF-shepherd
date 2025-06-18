import matplotlib.pyplot as plt
from config import *

def plot_trajectories(start_positions, end_positions, agent_trajectories, shepherd_trajectory):
    plt.figure(figsize=(10, 8))
    
    # 初始化边界值
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    
    # 绘制Agent轨迹（灰色细线）
    for trajectory in agent_trajectories:
        x = [pos[0] for pos in trajectory]
        y = [pos[1] for pos in trajectory]
        plt.plot(x, y, color="gray", linewidth=0.5, alpha=0.5)
        min_x = min(min_x, min(x))
        max_x = max(max_x, max(x))
        min_y = min(min_y, min(y))
        max_y = max(max_y, max(y))
    
    # 绘制起始/结束位置（红色圆圈）
    for start, end in zip(start_positions, end_positions):
        plt.scatter(start[0], start[1], s=30, facecolors="none", 
                   edgecolors="red", linewidths=0.8, marker="o")
        plt.scatter(end[0], end[1], s=30, facecolors="none",
                   edgecolors="red", linewidths=0.8, marker="o")
        min_x = min(min_x, start[0], end[0])
        max_x = max(max_x, start[0], end[0])
        min_y = min(min_y, start[1], end[1])
        max_y = max(max_y, start[1], end[1])
    
    # 绘制牧羊犬轨迹（蓝色粗线）
    x_shepherd = [pos[0] for pos in shepherd_trajectory]
    y_shepherd = [pos[1] for pos in shepherd_trajectory]
    plt.plot(x_shepherd, y_shepherd, color="blue", linewidth=1.5, alpha=0.8)
    min_x = min(min_x, min(x_shepherd))
    max_x = max(max_x, max(x_shepherd))
    min_y = min(min_y, min(y_shepherd))
    max_y = max(max_y, max(y_shepherd))

    # 绘制目标区域
    plt.scatter(TARGET[0], TARGET[1], s=TARGET_RADIUS, marker="x", color="green")
    min_x = min(min_x, TARGET[0])
    max_x = max(max_x, TARGET[0])
    min_y = min(min_y, TARGET[1])
    max_y = max(max_y, TARGET[1])
    
    # 边距
    margin_x = 0.1 * (max_x - min_x) if max_x - min_x != 0 else 1
    margin_y = 0.1 * (max_y - min_y) if max_y - min_y != 0 else 1

    
    # 设置图形参数
    plt.title("Path of Agent and Shepherd")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.axis("equal")
    plt.xlim(min_x - margin_x, max_x + margin_x)
    plt.ylim(min_y - margin_y, max_y + margin_y)
    plt.show()
