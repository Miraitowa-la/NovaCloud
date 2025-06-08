from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from accounts.models import Role
from django.db.models import Q

class Command(BaseCommand):
    help = '创建默认角色：\"超级管理员\"和\"普通用户\"'

    def handle(self, *args, **options):
        # 获取所有权限
        all_permissions = Permission.objects.all()
        
        # 获取物联网设备和策略引擎相关的权限
        iot_strategy_permissions = Permission.objects.filter(
            Q(content_type__app_label='iot_devices') | 
            Q(content_type__app_label='strategy_engine')
        )
        
        # 创建或获取超级管理员角色
        admin_role, admin_created = Role.objects.get_or_create(
            codename='super_admin',
            defaults={
                'name': '超级管理员',
                'description': '拥有系统所有权限的角色',
                'is_system': True  # 标记为系统角色
            }
        )
        
        # 如果是现有角色，确保它被标记为系统角色
        if not admin_created:
            admin_role.is_system = True
            admin_role.save()
        
        # 更新权限
        admin_role.permissions.set(all_permissions)
        self.stdout.write(self.style.SUCCESS(f'已{"创建" if admin_created else "更新"} 超级管理员角色'))
        
        # 创建或获取普通用户角色
        normal_role, normal_created = Role.objects.get_or_create(
            codename='normal_user',
            defaults={
                'name': '普通用户',
                'description': '拥有物联网设备和策略引擎相关权限的角色',
                'is_system': True  # 标记为系统角色
            }
        )
        
        # 如果是现有角色，确保它被标记为系统角色
        if not normal_created:
            normal_role.is_system = True
            normal_role.save()
        
        # 更新权限
        normal_role.permissions.set(iot_strategy_permissions)
        self.stdout.write(self.style.SUCCESS(f'已{"创建" if normal_created else "更新"} 普通用户角色')) 