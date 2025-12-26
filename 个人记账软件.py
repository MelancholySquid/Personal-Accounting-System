import mysql.connector
import datetime
import getpass
from typing import List, Tuple, Dict, Any

class PersonalAccountingSystem:
    def __init__(self):
        self.connection = None
        self.current_user = None
        self.connect_database()
        self.create_tables()
    
    def connect_database(self):
        """连接MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='***',
                password='***',
                database='personal_accounting'
            )
            print('数据库连接成功')
        except mysql.connector.Error as err:
            print(f'数据库连接失败: {err}')
            exit(1)
    
    def create_tables(self):
        """创建必要的数据库表"""
        cursor = self.connection.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建收入记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                category ENUM('医疗', '饮食', '交通', '购物', '其他') NOT NULL,
                record_date DATE NOT NULL,
                remark TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')
        
        # 创建支出记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                category ENUM('医疗', '饮食', '交通', '购物', '其他') NOT NULL,
                record_date DATE NOT NULL,
                remark TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')
        
        self.connection.commit()
        cursor.close()
    
    def user_register(self) -> str:
        """用户注册功能"""
        print('=== 用户注册 ===')
        username = input('用户名: ').strip()
        password = getpass.getpass('密码: ').strip()
        
        if not username or not password:
            return '用户名和密码不能为空'
        
        cursor = self.connection.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', 
                         (username, password))
            self.connection.commit()
            return f'用户 {username} 注册成功'
        except mysql.connector.IntegrityError:
            return '用户名已存在'
        finally:
            cursor.close()
    
    def user_login(self) -> str:
        """用户登录功能"""
        print('=== 用户登录 ===')
        username = input('用户名: ').strip()
        password = getpass.getpass('密码: ').strip()
        
        cursor = self.connection.cursor()
        cursor.execute('SELECT username, password FROM users WHERE username = %s', (username,))
        result = cursor.fetchone()
        cursor.close()
        
        if result and result[1] == password:
            self.current_user = username
            return f'登录成功!欢迎 {username.upper()}'
        else:
            return '用户名或密码不正确'
    
    def add_income_record(self) -> str:
        """添加收入记录"""
        print('=== 添加收入 ===')
        try:
            amount = float(input('金额: '))
            print('类型: 1.医疗 2.饮食 3.交通 4.购物 5.其他')
            category_choice = input('请选择类型(1-5): ')
            categories = ['医疗', '饮食', '交通', '购物', '其他']
            category = categories[int(category_choice) - 1] if category_choice.isdigit() and 1 <= int(category_choice) <= 5 else '其他'
            
            record_date = input('日期(YYYY-MM-DD, 留空为今天): ').strip()
            if not record_date:
                record_date = datetime.datetime.now().strftime('%Y-%m-%d')
            
            remark = input('备注(可选): ').strip()
            
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO income_records (username, amount, category, record_date, remark)
                VALUES (%s, %s, %s, %s, %s)
            ''', (self.current_user, amount, category, record_date, remark))
            
            self.connection.commit()
            cursor.close()
            return '收入记录添加成功'
        except (ValueError, IndexError):
            return '输入数据格式错误'
    
    def add_expense_record(self) -> str:
        """添加支出记录"""
        print('=== 添加支出 ===')
        try:
            amount = float(input('金额: '))
            print('类型: 1.医疗 2.饮食 3.交通 4.购物 5.其他')
            category_choice = input('请选择类型(1-5): ')
            categories = ['医疗', '饮食', '交通', '购物', '其他']
            category = categories[int(category_choice) - 1] if category_choice.isdigit() and 1 <= int(category_choice) <= 5 else '其他'
            
            record_date = input('日期(YYYY-MM-DD, 留空为今天): ').strip()
            if not record_date:
                record_date = datetime.datetime.now().strftime('%Y-%m-%d')
            
            remark = input('备注(可选): ').strip()
            
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO expense_records (username, amount, category, record_date, remark)
                VALUES (%s, %s, %s, %s, %s)
            ''', (self.current_user, amount, category, record_date, remark))
            
            self.connection.commit()
            cursor.close()
            return '支出记录添加成功'
        except (ValueError, IndexError):
            return '输入数据格式错误'
    
    def view_all_records(self) -> str:
        """查看所有记录"""
        cursor = self.connection.cursor()
        
        # 查询收入记录
        cursor.execute('''
            SELECT id, amount, category, record_date, remark 
            FROM income_records 
            WHERE username = %s 
            ORDER BY record_date DESC
        ''', (self.current_user,))
        income_records = cursor.fetchall()
        
        # 查询支出记录
        cursor.execute('''
            SELECT id, amount, category, record_date, remark 
            FROM expense_records 
            WHERE username = %s 
            ORDER BY record_date DESC
        ''', (self.current_user,))
        expense_records = cursor.fetchall()
        
        cursor.close()
        
        result = '=== 所有收支记录 ===\n'
        result += '\n收入记录:\n'
        result += 'ID\t金额\t类型\t日期\t\t备注\n'
        for record in income_records:
            result += f"{record[0]}\t{record[1]}\t{record[2]}\t{record[3]}\t{record[4] or ''}\n"
        
        result += '\n支出记录:\n'
        result += 'ID\t金额\t类型\t日期\t\t备注\n'
        for record in expense_records:
            result += f"{record[0]}\t{record[1]}\t{record[2]}\t{record[3]}\t{record[4] or ''}\n"
        
        return result
    
    def modify_record(self) -> str:
        """修改记录"""
        print('=== 修改记录 ===')
        record_type = input('记录类型(1.收入 2.支出): ')
        record_id = input('记录ID: ')
        
        if record_type == '1':
            table_name = 'income_records'
        elif record_type == '2':
            table_name = 'expense_records'
        else:
            return '无效的记录类型'
        
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM {table_name} WHERE id = %s AND username = %s', 
                     (record_id, self.current_user))
        record = cursor.fetchone()
        
        if not record:
            cursor.close()
            return '记录不存在或无权修改'
        
        try:
            amount = input(f'新金额(原:{record[2]}): ').strip()
            amount = float(amount) if amount else record[2]
            
            print('新类型: 1.医疗 2.饮食 3.交通 4.购物 5.其他')
            category_choice = input(f'新类型(原:{record[3]}): ').strip()
            categories = ['医疗', '饮食', '交通', '购物', '其他']
            category = categories[int(category_choice) - 1] if category_choice.isdigit() and 1 <= int(category_choice) <= 5 else record[3]
            
            record_date = input(f'新日期(原:{record[4]}): ').strip()
            record_date = record_date if record_date else record[4]
            
            remark = input(f'新备注(原:{record[5] or ""}): ').strip()
            remark = remark if remark else record[5]
            
            cursor.execute(f'''
                UPDATE {table_name} 
                SET amount = %s, category = %s, record_date = %s, remark = %s 
                WHERE id = %s AND username = %s
            ''', (amount, category, record_date, remark, record_id, self.current_user))
            
            self.connection.commit()
            cursor.close()
            return '记录修改成功'
        except (ValueError, IndexError):
            cursor.close()
            return '输入数据格式错误'
    
    def delete_record(self) -> str:
        """删除记录"""
        print('=== 删除记录 ===')
        record_type = input('记录类型(1.收入 2.支出): ')
        record_id = input('记录ID: ')
        
        if record_type == '1':
            table_name = 'income_records'
        elif record_type == '2':
            table_name = 'expense_records'
        else:
            return '无效的记录类型'
        
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM {table_name} WHERE id = %s AND username = %s', 
                     (record_id, self.current_user))
        record = cursor.fetchone()
        
        if not record:
            cursor.close()
            return '记录不存在或无权删除'
        
        cursor.execute(f'DELETE FROM {table_name} WHERE id = %s AND username = %s', 
                     (record_id, self.current_user))
        self.connection.commit()
        cursor.close()
        
        return '记录删除成功'
    
    def query_records_by_date_range(self) -> str:
        """按日期段查询记录"""
        print('=== 按日期段查询 ===')
        start_date = input('起始日期(YYYY-MM-DD): ')
        end_date = input('结束日期(YYYY-MM-DD): ')
        record_type = input('记录类型(1.收入 2.支出): ')
        
        if record_type == '1':
            table_name = 'income_records'
            type_name = '收入'
        elif record_type == '2':
            table_name = 'expense_records'
            type_name = '支出'
        else:
            return '无效的记录类型'
        
        cursor = self.connection.cursor()
        cursor.execute(f'''
            SELECT id, amount, category, record_date, remark 
            FROM {table_name} 
            WHERE username = %s AND record_date BETWEEN %s AND %s 
            ORDER BY record_date
        ''', (self.current_user, start_date, end_date))
        
        records = cursor.fetchall()
        cursor.close()
        
        result = f'=== {start_date} 至 {end_date} {type_name}记录 ===\n'
        result += 'ID\t金额\t类型\t日期\t\t备注\n'
        for record in records:
            result += f"{record[0]}\t{record[1]}\t{record[2]}\t{record[3]}\t{record[4] or ''}\n"
        
        return result
    
    def statistics_by_date_range(self) -> str:
        """按日期段统计收入和支出"""
        print('=== 按日期段统计 ===')
        start_date = input('起始日期(YYYY-MM-DD): ')
        end_date = input('结束日期(YYYY-MM-DD): ')
        
        cursor = self.connection.cursor()
        
        # 统计收入
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM income_records 
            WHERE username = %s AND record_date BETWEEN %s AND %s
        ''', (self.current_user, start_date, end_date))
        total_income = cursor.fetchone()[0]
        
        # 统计支出
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM expense_records 
            WHERE username = %s AND record_date BETWEEN %s AND %s
        ''', (self.current_user, start_date, end_date))
        total_expense = cursor.fetchone()[0]
        
        cursor.close()
        
        result = f'=== {start_date} 至 {end_date} 统计结果 ===\n'
        result += f'总收入: {total_income:.2f}\n'
        result += f'总支出: {total_expense:.2f}\n'
        result += f'净收入: {(total_income - total_expense):.2f}\n'
        
        return result
    
    def statistics_by_category(self) -> str:
        """按类别统计收入和支出"""
        cursor = self.connection.cursor()
        
        # 按类别统计收入
        cursor.execute('''
            SELECT category, COALESCE(SUM(amount), 0) 
            FROM income_records 
            WHERE username = %s 
            GROUP BY category
        ''', (self.current_user,))
        income_by_category = cursor.fetchall()
        
        # 按类别统计支出
        cursor.execute('''
            SELECT category, COALESCE(SUM(amount), 0) 
            FROM expense_records 
            WHERE username = %s 
            GROUP BY category
        ''', (self.current_user,))
        expense_by_category = cursor.fetchall()
        
        cursor.close()
        
        result = '=== 按类别统计 ===\n'
        result += '\n收入统计:\n'
        result += '类型\t金额\n'
        for category, amount in income_by_category:
            result += f'{category}\t{amount:.2f}\n'
        
        result += '\n支出统计:\n'
        result += '类型\t金额\n'
        for category, amount in expense_by_category:
            result += f'{category}\t{amount:.2f}\n'
        
        return result
    
    def accounting_management_menu(self):
        """记账管理菜单"""
        while True:
            print('=== 记账管理 ===')
            print('1.添加收入')
            print('2.添加支出')
            print('3.查看所有记录')
            print('4.修改记录')
            print('5.删除记录')
            print('6.返回上级')
            
            choice = input('请选择操作: ').strip()
            
            if choice == '1':
                result = self.add_income_record()
                print(result)
            elif choice == '2':
                result = self.add_expense_record()
                print(result)
            elif choice == '3':
                result = self.view_all_records()
                print(result)
            elif choice == '4':
                result = self.modify_record()
                print(result)
            elif choice == '5':
                result = self.delete_record()
                print(result)
            elif choice == '6':
                break
            else:
                print('无效选择，请重新输入')
    
    def statistics_menu(self):
        """统计查询菜单"""
        while True:
            print('=== 统计查询 ===')
            print('1.按日期段查询记录')
            print('2.按日期段统计收支')
            print('3.按类别统计收支')
            print('4.返回上级')
            
            choice = input('请选择操作: ').strip()
            
            if choice == '1':
                result = self.query_records_by_date_range()
                print(result)
            elif choice == '2':
                result = self.statistics_by_date_range()
                print(result)
            elif choice == '3':
                result = self.statistics_by_category()
                print(result)
            elif choice == '4':
                break
            else:
                print('无效选择，请重新输入')
    
    def user_menu(self):
        """用户菜单"""
        while True:
            print('=== 用户菜单 ===')
            print('1.记账管理')
            print('2.统计查询')
            print('3.用户注销')
            
            choice = input('请选择操作: ').strip()
            
            if choice == '1':
                self.accounting_management_menu()
            elif choice == '2':
                self.statistics_menu()
            elif choice == '3':
                self.current_user = None
                print('用户已注销')
                break
            else:
                print('无效选择，请重新输入')
    
    def main_menu(self):
        """主菜单"""
        while True:
            print('=== 主菜单 ===')
            print('1.用户登录')
            print('2.用户注册')
            print('3.退出程序')
            
            choice = input('请选择操作: ').strip()
            
            if choice == '1':
                result = self.user_login()
                print(result)
                if self.current_user:
                    self.user_menu()
            elif choice == '2':
                result = self.user_register()
                print(result)
            elif choice == '3':
                print('程序退出，再见!')
                if self.connection:
                    self.connection.close()
                break
            else:
                print('无效选择，请重新输入')

def main():
    """主函数"""
    system = PersonalAccountingSystem()
    system.main_menu()
    return '个人记账系统运行完成'

if __name__ == '__main__':
    main()

