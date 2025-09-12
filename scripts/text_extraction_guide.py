#!/usr/bin/env python3
"""
文本内容提取功能使用指南
============================

本脚本演示了如何使用 core/web2md/gzh_url2md.py 中的新函数
来提取网页文本内容，特别是微信公众号文章。

主要功能：
1. extract_text_content() - 提取单个网页的文本内容
2. get_text_length_from_csv() - 批量处理CSV文件中的URL
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, 'core', 'web2md'))

from gzh_url2md import extract_text_content, get_text_length_from_csv


def demo_single_url_extraction():
    """演示单个URL文本提取"""
    print("=" * 60)
    print("单个URL文本提取演示")
    print("=" * 60)

    # 测试URL
    test_url = "https://mp.weixin.qq.com/s/BMIQe8HkEDmwXZGD12SgoA"

    print(f"正在处理URL: {test_url}")
    print("-" * 40)

    # 提取文本内容
    result = extract_text_content(test_url, include_stats=True)

    if result['success']:
        print("✓ 提取成功！")
        print(f"标题: {result['title']}")
        print(f"字符数: {result['char_count']}")
        print(f"字数: {result['word_count']}")
        print(f"预估阅读时间: {result['reading_time_minutes']} 分钟")

        # 显示内容预览
        print("\n内容预览（前300字符）:")
        print("-" * 30)
        preview = result['text'][:300] + "..." if len(result['text']) > 300 else result['text']
        print(preview)
    else:
        print(f"✗ 提取失败: {result.get('error', '未知错误')}")

    return result


def demo_csv_batch_processing():
    """演示CSV文件批量处理"""
    print("\n" + "=" * 60)
    print("CSV文件批量处理演示")
    print("=" * 60)

    # CSV文件路径
    csv_path = "../workspace/data/publish_history.csv"

    if os.path.exists(csv_path):
        print(f"找到CSV文件: {csv_path}")

        # 询问用户是否要处理完整文件
        response = input("是否要处理完整CSV文件？(y/N，仅处理前5条测试): ").strip().lower()

        if response == 'y':
            print("开始处理完整文件...")
            result_df = get_text_length_from_csv(csv_path, batch_size=5)
        else:
            print("仅处理前5条记录作为测试...")
            import pandas as pd

            # 读取并处理前5条记录
            df = pd.read_csv(csv_path)
            test_df = df.head(5).copy()

            # 保存临时测试文件
            test_csv_path = csv_path.replace('.csv', '_demo_sample.csv')
            test_df.to_csv(test_csv_path, index=False, encoding='utf-8-sig')

            # 处理测试文件
            result_df = get_text_length_from_csv(test_csv_path, batch_size=2)

            # 清理临时文件
            if os.path.exists(test_csv_path):
                os.remove(test_csv_path)
                print("临时测试文件已清理")

        if result_df is not None:
            print("✓ 批量处理完成")
            print(f"共处理 {len(result_df)} 条记录")

            # 显示处理结果统计
            success_count = len(result_df[result_df['提取状态'] == '成功'])
            print("
处理统计:"            print(f"成功提取: {success_count}/{len(result_df)} ({success_count/len(result_df)*100:.1f}%)")

            if success_count > 0:
                avg_words = result_df[result_df['正文字数'] > 0]['正文字数'].mean()
                print(f"平均字数: {avg_words:.0f}")

        else:
            print("✗ 批量处理失败")
    else:
        print(f"未找到CSV文件: {csv_path}")
        print("请确保文件存在，或修改脚本中的文件路径")


def demo_advanced_usage():
    """演示高级用法"""
    print("\n" + "=" * 60)
    print("高级用法演示")
    print("=" * 60)

    # 示例：自定义内容选择器
    urls = [
        "https://mp.weixin.qq.com/s/some-article-id",
        "https://example-blog.com/post/123",
    ]

    for url in urls:
        print(f"\n处理: {url}")

        # 只获取基本信息，不包含统计
        result = extract_text_content(url, include_stats=False)

        if result['success']:
            print(f"✓ 成功提取 {len(result['text'])} 字符的内容")
        else:
            print(f"✗ 提取失败: {result.get('error', '未知错误')}")


def main():
    """主函数"""
    print("文本内容提取功能使用指南")
    print("=" * 60)
    print("本演示将展示如何使用新的文本提取功能")
    print()

    try:
        # 演示1: 单个URL提取
        demo_single_url_extraction()

        # 演示2: CSV批量处理
        demo_csv_batch_processing()

        # 演示3: 高级用法
        demo_advanced_usage()

        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        print("\n使用提示:")
        print("1. 单个URL提取: extract_text_content(url, include_stats=True)")
        print("2. CSV批量处理: get_text_length_from_csv(csv_path, batch_size=5)")
        print("3. 可以通过 include_stats 参数控制是否返回统计信息")
        print("4. 函数会自动处理微信公众号文章的特殊结构")

    except KeyboardInterrupt:
        print("\n\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中出错: {e}")


if __name__ == "__main__":
    main()
