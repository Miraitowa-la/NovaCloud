from django.core.management.base import BaseCommand
from accounts.models import Role

class Command(BaseCommand):
    help = '更新系统角色的标记和创建者信息'

    def handle(self, *args, **options):
        # 获取系统角色
        try:
            super_admin_role = Role.objects.get(codename='super_admin')
            super_admin_role.is_system = True
            super_admin_role.save()
            self.stdout.write(self.style.SUCCESS(f'已将角色 "{super_admin_role.name}" 标记为系统角色'))
        except Role.DoesNotExist:
            self.stdout.write(self.style.WARNING('超级管理员角色不存在'))
        
        try:
            normal_user_role = Role.objects.get(codename='normal_user')
            normal_user_role.is_system = True
            normal_user_role.save()
            self.stdout.write(self.style.SUCCESS(f'已将角色 "{normal_user_role.name}" 标记为系统角色'))
        except Role.DoesNotExist:
            self.stdout.write(self.style.WARNING('普通用户角色不存在'))
        
        # 标记其他可能的系统角色
        self.stdout.write(self.style.SUCCESS('系统角色更新完成')) 