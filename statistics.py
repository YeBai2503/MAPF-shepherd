"""数据采样统计模块"""
from config import *
from agent import Agent
from shepherd import Shepherd
from utils import calculate_gcm
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import multiprocessing as mp
from functools import partial
import os

"""单次模拟"""
def simulation(seed=None):
    # 随机种子
    if seed is not None:
        np.random.seed(seed)
        
    # 统计量
    time_cost = 0 # 运行时间
    step_cost = 0 # 步数
    success = False # 是否成功

    start_time = time.time() 
    agents = [Agent(np.random.uniform(L/2, L, 2)) for _ in range(N)]
    shepherd = Shepherd()
    
    for step in range(MAX_STEPS):
        for agent in agents:
            agent.update(agents, shepherd.position)
        gcm = calculate_gcm(agents)
        shepherd.update(agents, gcm)
        if np.linalg.norm(gcm - TARGET) < TARGET_RADIUS:  
            success = True
            step_cost = step
            break
    
    time_cost = time.time() - start_time
    return time_cost, step_cost, success

"""统计分析"""
def analyze(data_array, title, unit=""):
    # 统计量
    mean_val = round(np.mean(data_array), 2)
    median_val = round(np.median(data_array), 2)
    percentile_50 = round(np.percentile(data_array, 50), 2)
    percentile_90 = round(np.percentile(data_array, 90), 2)
    percentile_95 = round(np.percentile(data_array, 95), 2)
    min_val = round(np.min(data_array), 2)
    max_val = round(np.max(data_array), 2)
    std_val = round(np.std(data_array), 2)
    
    # 打印统计结果
    print(f"\n——————— {title}统计分析 ———————")
    print(f"平均值: {mean_val} {unit}")
    print(f"中位数: {median_val} {unit}")
    print(f"标准差: {std_val} {unit}")
    print(f"最小值: {min_val} {unit}")
    print(f"最大值: {max_val} {unit}")
    print(f"50%分位数: {percentile_50} {unit}")
    print(f"90%分位数: {percentile_90} {unit}")
    print(f"95%分位数: {percentile_95} {unit}")
    
    # 创建图形
    plt.figure(figsize=(10, 6))
    # 直方图
    bins = min(20, len(data_array) // 2 + 1)  # 计算合适的bin数量
    plt.hist(data_array, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
    # 参数
    plt.xlabel(title)
    plt.ylabel('Frequency')
    plt.title(f'{title} Distribution Histogram')
    plt.grid(True, alpha=0.3)
    # 保存和显示
    plt.tight_layout()
    plt.savefig(f'{title}_histogram.png', dpi=300)
    plt.show()
    
    return {
        'mean': mean_val,
        'median': median_val,
        'std': std_val,
        'min': min_val,
        'max': max_val,
        'p50': percentile_50,
        'p90': percentile_90,
        'p95': percentile_95
    }

"""单进程模拟"""
def main_single_process():
    times = 100 # 模拟次数
    time_costs = [] # 时间
    step_costs = [] # 步数
    success_times = 0 # 成功次数

    # 模拟循环
    for i in range(times):
        sys.stdout.write(f"\r————————————进度: {i+1}/{times}————————————")
        sys.stdout.flush()
        time_cost, step_cost, success = simulation()
        time_costs.append(time_cost)
        step_costs.append(step_cost)
        if success:
            success_times += 1
            
    print()
    print(f"成功率: {success_times / times}")
    # 统计
    step_stats = analyze(step_costs, "Step")
    time_stats = analyze(time_costs, "Time", "s")

    # 保存到CSV文件
    filename = "simulation_statistics.csv"
    results = pd.DataFrame({
        '指标': ['平均值', '中位数', '标准差', '最小值', '最大值', '50%分位数', '90%分位数', '95%分位数'],
        '步数': [step_stats['mean'], step_stats['median'], step_stats['std'], 
                step_stats['min'], step_stats['max'], 
                step_stats['p50'], step_stats['p90'], step_stats['p95']],
        '时间(秒)': [time_stats['mean'], time_stats['median'], time_stats['std'], 
                    time_stats['min'], time_stats['max'], 
                    time_stats['p50'], time_stats['p90'], time_stats['p95']]
    })
    results.to_csv(filename, index=False)
    print(f"\n——————结果已保存到 {filename} ——————")

def simulation_wrapper(i):
    # 用进程ID和迭代索引创建种子
    seed = os.getpid() + i
    result = simulation(seed)
    return result

"""多进程模拟"""
def main_multiprocess():
    times = 100  # 模拟次数
    cpu_count = mp.cpu_count()
    print(f"将启动{min(cpu_count // 2, times)}个进程")
    results = [] # 结果
    
    # 创建进程池
    start_total = time.time()
    pool = mp.Pool(processes=min(cpu_count // 2, times))
    
    # 提交所有任务
    for i in range(times):
        results.append(pool.apply_async(simulation_wrapper, args=(i,)))
    
    # 等待任务完成并显示进度
    pool.close()
    completed = 0 # 完成次数
    while completed < times:
        completed = sum(1 for r in results if r.ready())
        sys.stdout.write(f"\r————————————进度: {completed}/{times}————————————")
        sys.stdout.flush()
        time.sleep(1)
    
    # 结果统计
    time_costs = []
    step_costs = []
    success_times = 0
    
    for result in results:
        time_cost, step_cost, success = result.get()
        time_costs.append(time_cost)
        step_costs.append(step_cost)
        if success:
            success_times += 1
    
    total_time = time.time() - start_total
    print(f"\n多进程总耗时: {total_time:.2f}秒")
    print(f"成功率: {success_times / times}")
    
    # 统计
    step_stats = analyze(step_costs, "Step")
    time_stats = analyze(time_costs, "Time", "s")

    # 保存到CSV文件
    filename = "simulation_statistics.csv"
    results = pd.DataFrame({
        '指标': ['平均值', '中位数', '标准差', '最小值', '最大值', '50%分位数', '90%分位数', '95%分位数'],
        '步数': [step_stats['mean'], step_stats['median'], step_stats['std'], 
                step_stats['min'], step_stats['max'], 
                step_stats['p50'], step_stats['p90'], step_stats['p95']],
        '时间(秒)': [time_stats['mean'], time_stats['median'], time_stats['std'], 
                    time_stats['min'], time_stats['max'], 
                    time_stats['p50'], time_stats['p90'], time_stats['p95']]
    })
    results.to_csv(filename, index=False)
    print(f"\n——————结果已保存到 {filename} ——————")

def main():
    # 默认用多进程版本进行模拟
    use_multiprocess = True
    
    if use_multiprocess:
        print("————————————————多进程运行————————————————")
        main_multiprocess() 
    else:
        print("————————————————单进程运行————————————————")
        main_single_process()

if __name__ == "__main__":
    main()