import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# df = pd.read_csv('sales_data.csv')
# 设置中文字体显示（MacOS系统）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # MacOS常用中文字体，如果是windows，则使用SimHei
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
# 生成模拟销售数据
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
sales = np.random.randint(100, 1000, size=len(dates))
products = np.random.choice(['A', 'B', 'C', 'D'], size=len(dates))

df = pd.DataFrame({
    'date': dates,
    'sales': sales,
    'product': products
})

# 随机添加一些缺失值
mask = np.random.random(len(df)) < 0.05
df.loc[mask, 'sales'] = np.nan
df = df.dropna()
df['date'] = pd.to_datetime(df['date'])

monthly_sales = df.groupby(df['date'].dt.month)['sales'].sum()

plt.figure(figsize=(12, 8), facecolor='#f5f5f5')
sns.set_palette("husl")

ax = sns.barplot(x=monthly_sales.index, y=monthly_sales.values,
                edgecolor='black', linewidth=1.2)

plt.title('月度销售数据', fontsize=16, pad=20)
plt.xlabel('月份', fontsize=12)
plt.ylabel('销售总额', fontsize=12)

# 添加数据标签
for p in ax.patches:
    ax.annotate(f'{int(p.get_height()):,}',
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center',
                xytext=(0, 10),
                textcoords='offset points',
                fontsize=10)

plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()