#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NovaCloud项目数据库清理工具

此脚本用于清空NovaCloud项目SQLite数据库中的特定数据。
在执行前会要求用户确认，以防意外删除数据。
"""

import os
import sys
import importlib.util
import django

# 检查脚本是否在项目根目录运行
if not os.path.exists('manage.py'):
    print("错误：请在项目根目录（包含manage.py的目录）中运行此脚本。")
    sys.exit(1)

# 添加当前目录到Python路径，确保能找到项目模块
current_dir = os.path.abspath('.')
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    print(f"已将当前目录添加到Python路径: {current_dir}")

# 自动检测Django项目设置模块
def detect_settings_module():
    """
    自动检测Django项目的设置模块路径
    通过多种策略尝试找到正确的设置模块
    """
    try:
        # 策略1: 从manage.py文件分析
        settings_module = None
        if os.path.exists('manage.py'):
            with open('manage.py', 'r') as f:
                content = f.read()
                
            import re
            settings_patterns = [
                r"os\.environ\.setdefault\(['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"]([^'\"]+)['\"]",
                r"DJANGO_SETTINGS_MODULE['\"]?\s*=\s*['\"]([^'\"]+)['\"]"
            ]
            
            for pattern in settings_patterns:
                match = re.search(pattern, content)
                if match:
                    settings_module = match.group(1)
                    print(f"从manage.py文件检测到设置模块: {settings_module}")
                    # 检查该模块是否可导入
                    try:
                        importlib.import_module(settings_module)
                        return settings_module
                    except ImportError:
                        print(f"警告: 检测到的设置模块 '{settings_module}' 不能被导入，尝试其他方法...")
        
        # 策略2: 使用常见的默认值尝试
        project_name = os.path.basename(os.path.abspath('.'))
        potential_settings = [
            f"{project_name}.settings",  # 项目名.settings
            "config.settings",           # config.settings (常见配置)
            "app.settings",              # app.settings
            "settings",                  # 直接settings模块
            "src.settings"               # src.settings
        ]
        
        # 如果前面从manage.py检测到了设置但导入失败，尝试修复常见错误
        if settings_module:
            # 如果是形如"project.settings.base"或"project.settings.local"的格式
            if '.' in settings_module:
                base_module = settings_module.split('.')[0]
                potential_settings.insert(0, f"{base_module}.settings")
        
        print("尝试常见的设置模块路径...")
        for settings_path in potential_settings:
            try:
                print(f"  尝试: {settings_path}")
                importlib.import_module(settings_path)
                print(f"  √ 成功: {settings_path}")
                return settings_path
            except ImportError:
                pass
                
        # 策略3: 扫描文件系统查找settings.py文件
        print("扫描项目目录查找settings.py文件...")
        found_settings_files = []
        for root, dirs, files in os.walk('.'):
            if 'settings.py' in files and '.venv' not in root and '__pycache__' not in root and '.git' not in root:
                rel_path = os.path.relpath(root, '.')
                if rel_path == '.':
                    # settings.py 在根目录
                    potential_module = 'settings'
                else:
                    # 将路径转换为Python模块路径
                    potential_module = rel_path.replace(os.sep, '.') + '.settings'
                
                found_settings_files.append((potential_module, os.path.join(rel_path, 'settings.py')))
                
        if found_settings_files:
            print("\n找到以下settings.py文件:")
            for i, (module_path, file_path) in enumerate(found_settings_files, 1):
                print(f"  {i}. {module_path} ({file_path})")
            
            if len(found_settings_files) == 1:
                # 只有一个选项，直接尝试使用
                settings_path = found_settings_files[0][0]
                try:
                    importlib.import_module(settings_path)
                    print(f"\n使用找到的唯一设置模块: {settings_path}")
                    return settings_path
                except ImportError as e:
                    print(f"警告: 无法导入找到的设置模块 '{settings_path}': {e}")
            else:
                # 有多个选项，让用户选择
                try:
                    choice = input("\n找到多个可能的设置文件，请选择一个(输入编号): ")
                    if choice.isdigit() and 1 <= int(choice) <= len(found_settings_files):
                        selected = found_settings_files[int(choice) - 1][0]
                        try:
                            importlib.import_module(selected)
                            return selected
                        except ImportError as e:
                            print(f"警告: 无法导入所选设置模块 '{selected}': {e}")
                    else:
                        print("无效的选择")
                except (KeyboardInterrupt, EOFError):
                    print("\n操作已取消")
                    sys.exit(0)
        
        # 所有自动检测方法失败，要求用户手动输入
        print("\n自动检测设置模块失败。请手动提供设置模块路径。")
        print("提示: 你可以查看manage.py文件中的'DJANGO_SETTINGS_MODULE'设置来找到正确的路径。")
        
        while True:
            try:
                settings_module = input("\n请输入Django设置模块路径 (例如 'myproject.settings'): ")
                if not settings_module:
                    print("设置模块路径不能为空!")
                    continue
                
                print(f"尝试导入设置模块: {settings_module}")
                importlib.import_module(settings_module)
                print("√ 导入成功!")
                return settings_module.strip()
            except ImportError as e:
                print(f"错误: 无法导入 '{settings_module}': {e}")
                print("请检查模块路径是否正确，然后重试，或按Ctrl+C取消操作。")
            except (KeyboardInterrupt, EOFError):
                print("\n操作已取消")
                sys.exit(0)
    except Exception as e:
        print(f"检测设置模块时出错: {e}")
        print("请手动提供正确的设置模块路径。")
        
        try:
            settings_module = input("请输入Django设置模块路径 (例如 'myproject.settings'): ")
            if settings_module:
                return settings_module.strip()
            else:
                print("设置模块路径不能为空，操作已取消。")
                sys.exit(1)
        except (KeyboardInterrupt, EOFError):
            print("\n操作已取消")
            sys.exit(0)

# 设置Django环境
try:
    # 尝试自动检测设置模块
    settings_module = detect_settings_module()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    
    print(f"\n正在使用设置模块: {settings_module}")
    print("初始化Django环境...")
    django.setup()
    print("Django环境初始化成功!")
except Exception as e:
    print(f"\n设置Django环境时出错: {e}")
    print("\n可能的解决方案:")
    print("1. 确保你在项目根目录(包含manage.py的目录)中运行此脚本")
    print("2. 确保Django项目已正确安装和配置")
    print("3. 查看manage.py文件确定正确的设置模块路径")
    print("4. 确保设置模块及其依赖可从当前环境中导入")
    print("5. 如果使用虚拟环境，确保已激活正确的虚拟环境")
    
    # 显示当前Python路径，帮助诊断
    print("\n当前Python路径(sys.path):")
    for i, path in enumerate(sys.path, 1):
        print(f"  {i}. {path}")
    
    sys.exit(1)

# 导入需要操作的模型
try:
    print("\n导入Django模型...")
    from django.contrib.auth.models import User
    from accounts.models import UserProfile, Role, InvitationCode
    from iot_devices.models import Project, Device, Sensor, Actuator, SensorData, ActuatorCommandLog
    from strategy_engine.models import Strategy, ConditionGroup, Condition, Action, ExecutionLog
    from core.models import AuditLog
    
    print("所有模型导入成功!")
except ImportError as e:
    print(f"\n导入模型时出错: {e}")
    print("\n可能的解决方案:")
    print("1. 确保所有应用已添加到INSTALLED_APPS中")
    print("2. 确保你的虚拟环境中安装了所有必要的依赖")
    print("3. 检查模型导入路径是否正确")
    print("4. 检查项目结构是否与脚本预期的一致")
    sys.exit(1)

def clear_data():
    """
    按照合适的顺序清空数据库中的数据，
    避免外键约束错误
    """
    print("\n正在清空数据库数据...\n")

    # 1. 首先清理策略引擎相关数据（这些通常是叶子节点）
    print("===== 清理策略引擎数据 =====")
    deleted_count = ExecutionLog.objects.all().delete()
    print(f"已清除 ExecutionLog 数据: {deleted_count}")
    
    deleted_count = Action.objects.all().delete()
    print(f"已清除 Action 数据: {deleted_count}")
    
    deleted_count = Condition.objects.all().delete()
    print(f"已清除 Condition 数据: {deleted_count}")
    
    deleted_count = ConditionGroup.objects.all().delete()
    print(f"已清除 ConditionGroup 数据: {deleted_count}")
    
    deleted_count = Strategy.objects.all().delete()
    print(f"已清除 Strategy 数据: {deleted_count}")

    # 2. 清理物联网数据和传感器记录（数据记录先于设备实体）
    print("\n===== 清理物联网数据 =====")
    deleted_count = SensorData.objects.all().delete()
    print(f"已清除 SensorData 数据: {deleted_count}")
    
    deleted_count = ActuatorCommandLog.objects.all().delete()
    print(f"已清除 ActuatorCommandLog 数据: {deleted_count}")
    
    # 3. 清理物联网实体，Project会级联删除其下的Device、Sensor和Actuator
    deleted_count = Project.objects.all().delete()
    print(f"已清除 Project、Device、Sensor和Actuator数据（级联删除）: {deleted_count}")

    # 4. 清理用户相关数据
    print("\n===== 清理用户和系统数据 =====")
    deleted_count = InvitationCode.objects.all().delete()
    print(f"已清除 InvitationCode 数据: {deleted_count}")
    
    deleted_count = AuditLog.objects.all().delete()
    print(f"已清除 AuditLog 数据: {deleted_count}")
    
    # 5. 清理用户和角色
    # 如果要保留超级用户，可以使用：User.objects.filter(is_superuser=False).delete()
    deleted_count = User.objects.all().delete()  # 这会级联删除 UserProfile
    print(f"已清除 User 和 UserProfile 数据: {deleted_count}")
    
    deleted_count = Role.objects.all().delete()
    print(f"已清除 Role 数据: {deleted_count}")
    
    print("\n数据库清理完成！\n")

def show_warning():
    """显示警告信息并获取用户确认"""
    print("=" * 80)
    print("警告: 此操作将清空数据库中的所有数据！")
    print("此操作不可撤销，请确保你已备份重要数据。")
    print("=" * 80)
    
    try:
        confirm = input("\n请输入 'yes' 确认继续操作，或任意其他键取消: ")
        return confirm.lower() == 'yes'
    except KeyboardInterrupt:
        print("\n操作已取消。")
        return False

if __name__ == '__main__':
    print("\nNovaCloud项目数据库清理工具")
    print("-" * 30)
    
    if show_warning():
        try:
            clear_data()
        except Exception as e:
            print(f"清理过程中出错: {e}")
            sys.exit(1)
    else:
        print("操作已取消，未对数据库进行任何更改。")
        sys.exit(0) 