#!/usr/bin/env python3
"""
河流图可视化使用示例
演示如何使用新创建的河流图可视化功能
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def create_realistic_sample_data():
    """创建更真实的示例数据"""
    print("📊 创建真实示例数据...")
    
    # 创建示例账号
    accounts = ['AGI观察室', 'AGI启示录', 'AI万象志', '人工智能漫游指南']
    
    # 创建时间范围（最近6个月）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # 生成示例数据
    data = []
    for i in range(200):  # 生成200条记录
        # 随机选择账号
        account = np.random.choice(accounts)
        
        # 随机生成时间（偏向工作日）
        random_days = np.random.randint(0, 180)
        publish_time = start_date + timedelta(days=random_days)
        
        # 如果是周末，减少发布概率
        if publish_time.weekday() >= 5:  # 周六、周日
            if np.random.random() > 0.3:  # 70%概率跳过
                continue
        
        # 生成阅读量（基于账号的基准值和时间趋势）
        base_reads = {
            'AGI观察室': 1200,
            'AGI启示录': 900,
            'AI万象志': 700,
            '人工智能漫游指南': 500
        }
        
        # 添加时间趋势（周末阅读量较低）
        time_factor = 0.7 if publish_time.weekday() >= 5 else 1.0
        
        # 添加随机波动
        reads = int(base_reads[account] * time_factor * np.random.uniform(0.5, 1.8))
        reads = max(0, reads)  # 确保非负
        
        # 生成其他指标（与阅读量相关）
        likes = int(reads * np.random.uniform(0.02, 0.08))
        shares = int(reads * np.random.uniform(0.01, 0.05))
        
        # 生成标题
        titles = [
            "AI技术的最新发展趋势",
            "人工智能在医疗领域的应用",
            "机器学习算法优化实践",
            "深度学习模型训练技巧",
            "自然语言处理技术解析",
            "计算机视觉应用案例",
            "AI伦理与安全思考",
            "人工智能未来展望"
        ]
        
        data.append({
            '发布时间': publish_time.strftime('%Y-%m-%d'),
            '阅读量': reads,
            '点赞量': likes,
            '分享量': shares,
            '账号名称': account,
            '标题': np.random.choice(titles),
            '链接': f'https://example.com/article_{i+1}'
        })
    
    return pd.DataFrame(data)

def demonstrate_data_analysis():
    """演示数据分析功能"""
    print("🔍 演示数据分析功能...")
    
    # 创建示例数据
    df = create_realistic_sample_data()
    
    print(f"📊 数据概览:")
    print(f"   - 总记录数: {len(df)}")
    print(f"   - 时间范围: {df['发布时间'].min()} 到 {df['发布时间'].max()}")
    print(f"   - 账号数量: {len(df['账号名称'].unique())}")
    print(f"   - 总阅读量: {df['阅读量'].sum():,}")
    print(f"   - 平均阅读量: {df['阅读量'].mean():.1f}")
    
    # 按账号统计
    print(f"\n📈 各账号表现:")
    account_stats = df.groupby('账号名称').agg({
        '阅读量': ['count', 'sum', 'mean'],
        '点赞量': 'sum',
        '分享量': 'sum'
    }).round(1)
    
    for account in df['账号名称'].unique():
        account_data = df[df['账号名称'] == account]
        print(f"   - {account}:")
        print(f"     * 文章数: {len(account_data)}")
        print(f"     * 总阅读量: {account_data['阅读量'].sum():,}")
        print(f"     * 平均阅读量: {account_data['阅读量'].mean():.1f}")
        print(f"     * 总点赞量: {account_data['点赞量'].sum():,}")
        print(f"     * 总分享量: {account_data['分享量'].sum():,}")
    
    # 按时间统计
    print(f"\n📅 时间趋势分析:")
    df['发布时间'] = pd.to_datetime(df['发布时间'])
    df['月份'] = df['发布时间'].dt.to_period('M')
    
    monthly_stats = df.groupby('月份').agg({
        '阅读量': ['count', 'sum', 'mean']
    }).round(1)
    
    for month in df['月份'].unique():
        month_data = df[df['月份'] == month]
        print(f"   - {month}:")
        print(f"     * 文章数: {len(month_data)}")
        print(f"     * 总阅读量: {month_data['阅读量'].sum():,}")
        print(f"     * 平均阅读量: {month_data['阅读量'].mean():.1f}")
    
    return df

def demonstrate_visualization_preparation():
    """演示可视化数据准备"""
    print("📈 演示可视化数据准备...")
    
    # 加载数据
    df = create_realistic_sample_data()
    df['发布时间'] = pd.to_datetime(df['发布时间'])
    
    # 演示不同时间粒度的数据处理
    time_granularities = {
        'daily': '日',
        'weekly': '周', 
        'monthly': '月'
    }
    
    for granularity, name in time_granularities.items():
        print(f"\n📊 {name}粒度数据处理:")
        
        if granularity == 'daily':
            df['时间分组'] = df['发布时间'].dt.date
        elif granularity == 'weekly':
            df['时间分组'] = df['发布时间'].dt.to_period('W').dt.start_time.dt.date
        elif granularity == 'monthly':
            df['时间分组'] = df['发布时间'].dt.to_period('M').dt.start_time.dt.date
        
        # 按时间和账号分组聚合数据
        flow_data = df.groupby(['时间分组', '账号名称'])['阅读量'].sum().reset_index()
        
        # 创建透视表
        pivot_data = flow_data.pivot(index='时间分组', columns='账号名称', values='阅读量').fillna(0)
        
        print(f"   - 数据形状: {pivot_data.shape}")
        print(f"   - 时间范围: {pivot_data.index.min()} 到 {pivot_data.index.max()}")
        print(f"   - 账号列表: {list(pivot_data.columns)}")
        print(f"   - 总阅读量: {pivot_data.sum().sum():,}")
        
        # 显示前几行数据
        print(f"   - 前5行数据:")
        print(pivot_data.head().to_string())
    
    return True

def demonstrate_chart_types():
    """演示不同图表类型的特点"""
    print("🎨 演示不同图表类型的特点...")
    
    chart_types = {
        "基础图表": [
            "面积图 (Area Chart) - 显示趋势和总量",
            "流图 (Stream Chart) - 平滑的河流效果",
            "山脊图 (Ridge Plot) - 每个账号独立显示"
        ],
        "高级图表": [
            "高级流图 (Advanced Stream Chart) - 更平滑的曲线",
            "平行类别图 (Parallel Categories) - 多维度关系",
            "树状图 (Treemap) - 矩形大小表示数值",
            "冰柱图 (Icicle Chart) - 矩形层次布局"
        ],
        "专业河流图": [
            "河流图 (River Flow Chart) - 支持堆叠、分离、标准化三种模式",
            "山脊流图 (Ridge Flow Chart) - 山脊式河流图"
        ]
    }
    
    for category, charts in chart_types.items():
        print(f"\n📊 {category}:")
        for chart in charts:
            print(f"   - {chart}")
    
    return True

def main():
    """主演示函数"""
    print("🌊 河流图可视化功能使用示例")
    print("=" * 60)
    
    try:
        # 演示数据分析
        df = demonstrate_data_analysis()
        print()
        
        # 演示可视化数据准备
        demonstrate_visualization_preparation()
        print()
        
        # 演示图表类型
        demonstrate_chart_types()
        print()
        
        # 保存示例数据
        sample_file = "workspace/data/publish_history_for_calendar.csv"
        os.makedirs(os.path.dirname(sample_file), exist_ok=True)
        df.to_csv(sample_file, index=False, encoding='utf-8-sig')
        print(f"💾 示例数据已保存到: {sample_file}")
        
        print("=" * 60)
        print("🎉 演示完成！")
        print()
        print("📋 使用建议:")
        print("1. 启动Streamlit应用: streamlit run homepage.py")
        print("2. 导航到河流图可视化页面")
        print("3. 使用侧边栏调整参数")
        print("4. 选择不同的图表类型进行探索")
        print("5. 使用筛选功能聚焦特定数据")
        print()
        print("🚀 开始探索您的数据吧！")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
