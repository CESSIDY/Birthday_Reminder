from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivymd.uix.datatables import MDDataTable
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window
import datetime
from database import DataBase
from CostumeMDDatePecker import CostumeMDDatePicker


class DataBaseAdapter:
    def __init__(self, db_file=None):
        self.database = DataBase(db_file)

    def create_all_tables(self):
        sql_create_projects_table = """CREATE TABLE IF NOT EXISTS friends (
                                                id	INTEGER NOT NULL,
                                                first_name	TEXT,
                                                last_name	TEXT,
                                                birth_date	TEXT,
                                                PRIMARY KEY(id AUTOINCREMENT)
                                            );                                     
                                    """
        self.database.create_table(sql_create_projects_table)

    def isValid(self, data_turple):
        for val in data_turple:
            if not val:
                return False
        return True

    def clear_data(self, data_tuple):
        data_tuple = map(lambda v: str(v).replace(" ", ""), data_tuple)
        return data_tuple

    def insert_friend(self, data_tuple):
        sql = ''' INSERT INTO friends(first_name,last_name,birth_date)
                  VALUES(?,?,?) '''
        data_tuple = tuple(self.clear_data(data_tuple))
        if self.isValid(data_tuple):
            self.database.make_sql_command(sql, data_tuple)

    def update_friend_by_id(self, update_data_list, friend_id):
        sql = ''' UPDATE friends
                  SET first_name = ? ,
                      last_name = ? ,
                      birth_date = ?
                  WHERE id = ?'''

        update_data_list.append(friend_id)
        clean_data = tuple(self.clear_data(update_data_list))
        if self.isValid(clean_data):
            self.database.make_sql_command(sql, clean_data)

    def delete_friend_by_id(self, friend_id):
        sql = 'DELETE FROM friends WHERE id=?'
        data_tuple = (friend_id,)
        self.database.make_sql_command(sql, data_tuple)

    def select_all_friends(self):
        sql = "SELECT * FROM friends"
        friends = self.database.querying_data(sql)
        return friends

    def delete_friend_by_all_fields(self, data_list):
        sql = "DELETE FROM friends WHERE first_name=? AND last_name=? AND birth_date=?"
        self.database.make_sql_command(sql, data_list)

    def find_one_by_all_fields(self, data_list):
        sql = "SELECT * FROM friends WHERE first_name=? AND last_name=? AND birth_date=?"
        friend = self.database.querying_data(sql, data_list)
        return friend


class FriendTableGUI(MDDataTable):
    def __init__(self, friends, press_edit_func=None, press_remove_func=None):
        self.database_adapter = DataBaseAdapter()
        self.size_hint = (0.9, 0.9)
        self.use_pagination = True
        self.column_data = [
            ("Nr.", dp(10)),
            ("First name", dp(35)),
            ("Last name", dp(35)),
            ("Birthday", dp(30),),
        ]
        self.row_data = []
        self.change_data(friends)
        self.rows_num = 6
        self.sorted_on = "Birthday"
        self.sorted_order = "ASC"
        self.elevation = 2
        self.popup = None
        self.layout = BoxLayout(orientation='horizontal', spacing=5, padding=5)
        self.remove_button = Button(text="REMOVE", on_press=press_remove_func, background_color=[.69, .07, 0, 1],
                                    background_normal='')
        self.edit_button = Button(text="EDIT", on_press=press_edit_func, background_color=[.25, .59, .76, 1],
                                  background_normal='')
        super(FriendTableGUI, self).__init__()
        self.bind(on_row_press=self.action_on_row_press)

    def change_data(self, friends):
        # sorts in the order of the coming days and months
        rows_data = self.sort_data_by_month(friends)
        result_row_data = []
        # change index number for tables
        for key, row in enumerate(rows_data, start=1):
            result_row_data.append((str(key), row[1], row[2], row[3]))
        self.row_data = result_row_data

    def sort_data_by_month(self, rows_data):
        today = datetime.datetime.today()
        current_month = today.month
        current_day = today.day

        def sort_key(value):
            try:
                year, month, day = str(value[-1]).split("-")
            except ValueError:
                return ("", "")
            return (month, day)

        rows_data = sorted(rows_data, key=sort_key)
        lower_date = list()
        upper_date = list()
        for row in rows_data:
                try:
                    year, month, day = str(row[-1]).split("-")
                except ValueError:
                    continue
                if int(month) < current_month:
                    lower_date.append(row)
                    continue
                elif(int(month) == current_month) and (int(day) < current_day):
                    lower_date.append(row)
                    continue
                upper_date.append(row)
        rows_data = upper_date + lower_date
        return rows_data

    def action_on_row_press(self, instance_table, instance_row):
        result = list()

        for row_on_page in self.table_data.recycle_data:
            if str(row_on_page['Index']) == str(instance_row.index):
                result = list(filter(lambda x: x['range'] == row_on_page['range'], self.table_data.recycle_data))
                break

        self.layout.remove_widget(self.remove_button)
        self.layout.remove_widget(self.edit_button)
        self.layout = BoxLayout(orientation='horizontal', spacing=5, padding=5)
        self.remove_button.first_name = result[1]['text']
        self.remove_button.last_name = result[2]['text']
        self.remove_button.birth_date = result[3]['text']

        self.edit_button.first_name = result[1]['text']
        self.edit_button.last_name = result[2]['text']
        self.edit_button.birth_date = result[3]['text']

        self.layout.add_widget(self.remove_button)
        self.layout.add_widget(self.edit_button)

        self.popup = Popup(title='Row settings', content=self.layout, size_hint=(None, None), size=(220, 120))
        self.popup.open()


class FriendInputGUI:
    def __init__(self, base_layout, press_save_func=None):
        self.base_layout = base_layout
        self.database_adapter = DataBaseAdapter()
        self.first_name_label = Label(text="First name")
        self.first_name_input = TextInput(multiline=False,
                                          font_size=20)
        self.last_name_label = Label(text="Last name")
        self.last_name_input = TextInput(multiline=False,
                                         font_size=20)
        self.birthday_label = Label(text="Birthday")
        self.birthday_input = TextInput(multiline=False,
                                        font_size=20)
        self.birthday_input.bind(focus=self.open_date_picker)
        self.button_save = Button(text='SAVE', on_press=press_save_func)
        self.hidden_id = Label(text_size=(0, 0), size=(0, 0))
        self.combine_whit_layout()

    def combine_whit_layout(self):
        self.base_layout.add_widget(self.hidden_id)
        self.base_layout.add_widget(self.first_name_label)
        self.base_layout.add_widget(self.first_name_input)
        self.base_layout.add_widget(self.last_name_label)
        self.base_layout.add_widget(self.last_name_input)
        self.base_layout.add_widget(self.birthday_label)
        self.base_layout.add_widget(self.birthday_input)
        self.base_layout.add_widget(self.button_save)

    def save_in_database(self):
        data_list = [self.first_name_input.text, self.last_name_input.text, self.birthday_input.text]
        if self.hidden_id.text:
            self.database_adapter.update_friend_by_id(data_list, self.hidden_id.text)
        else:
            self.database_adapter.insert_friend(data_list)

        self.hidden_id.text = ""
        self.first_name_input.text = ""
        self.last_name_input.text = ""
        self.birthday_input.text = ""

    def open_date_picker(self, instance, value):
        if value:
            birthday_input_text = self.birthday_input.text
            year = None
            mount = None
            day = None
            if birthday_input_text:
                year, mount, day = map(lambda v: int(v), str(birthday_input_text).split("-"))
            picker = CostumeMDDatePicker(self.get_date_from_date_picker, year=year, month=mount, day=day)
            picker.open()

    def get_date_from_date_picker(self, the_date):
        try:
            self.birthday_input.text = str(the_date)
        except:
            pass


class FriendReminderGUI(Popup):
    def __init__(self, friends=None, **kwargs):
        if friends:
            self.friends = friends
        else:
            self.friends = DataBaseAdapter().select_all_friends()
        self.title = 'Happy Birthday LIST'
        self.content = self.get_content()
        self.size_hint = (None, None)
        self.size = (400, 400)
        self.auto_dismiss = True
        super(FriendReminderGUI, self).__init__(**kwargs)
    
    def open(self, *largs, **kwargs):
        super(FriendReminderGUI, self).open(*largs, **kwargs)
        Clock.schedule_once(self.dismiss, 10)

    
    @staticmethod
    def is_current_day(friend):
        if friend[-1]:
            year, month, day = str(friend[-1]).split("-")
            today = datetime.datetime.today()
            current_month = today.month
            current_day = today.day
            if int(month) == int(current_month) and int(day) == int(current_day):
                return True
        return False

    def press_close(self, instance):
        self.dismiss()

    def get_content(self):
        friends_birthday_now = list(filter(self.is_current_day, self.friends))
        if len(friends_birthday_now):
            layout = BoxLayout(orientation='vertical', spacing=5, padding=5)
            for friend in friends_birthday_now:
                layout.add_widget(Label(text=f"{friend[1]} {friend[2]}"))
            layout.add_widget(Button(text="CLOSE",
                                     on_press=self.press_close,
                                     background_color=[.69, .07, 0, 1],
                                     background_normal=''))

            return layout
        return Widget()


class BirthDayBaseGrid(Widget):
    def __new__(cls, *args, **kwargs):
        cls.gl_person_input = ObjectProperty(None, allownone=True)
        cls.al_persons_info = ObjectProperty(None, allownone=True)
        cls.gl_persons_scroll_info = ObjectProperty(None, allownone=True)
        return super(BirthDayBaseGrid, cls).__new__(cls, *args, **kwargs)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (1300, 500)
        self.database_adapter = DataBaseAdapter()
        self.database_adapter.create_all_tables()
        friends = self.database_adapter.select_all_friends()
        self.friendTableGUI = FriendTableGUI(friends=friends,
                                             press_edit_func=self.press_edit,
                                             press_remove_func=self.press_remove)
        self.al_persons_info.add_widget(self.friendTableGUI)
        self.friendInputGUI = FriendInputGUI(base_layout=self.gl_person_input,
                                             press_save_func=self.press_save)
        self.reminder_popup = FriendReminderGUI(friends=friends)
        today = datetime.datetime.today()
        seconds_until_next_day = ((24*60*60) - (((today.hour*60)*60) + (today.minute*60) + today.second))

        Clock.schedule_once(self.open_reminder, 15)
        Clock.schedule_once(self.open_reminder, seconds_until_next_day)

    def open_reminder(self, *args):
        self.reminder_popup.open()

    def refresh_table(self):
        self.al_persons_info.remove_widget(self.friendTableGUI)
        self.friendTableGUI = FriendTableGUI(friends=self.database_adapter.select_all_friends(),
                                             press_edit_func=self.press_edit,
                                             press_remove_func=self.press_remove)
        self.al_persons_info.add_widget(self.friendTableGUI)

    def press_remove(self, instance):
        data_list = [instance.first_name, instance.last_name, instance.birth_date]
        self.database_adapter.delete_friend_by_all_fields(data_list)
        self.friendTableGUI.popup.dismiss()
        self.refresh_table()

    def press_edit(self, instance):
        data_list = [instance.first_name, instance.last_name, instance.birth_date]
        self.friendInputGUI.first_name_input.text = instance.first_name
        self.friendInputGUI.last_name_input.text = instance.last_name
        self.friendInputGUI.birthday_input.text = instance.birth_date
        friend = self.database_adapter.find_one_by_all_fields(data_list)
        self.friendInputGUI.hidden_id.text = str(friend[0][0])
        self.friendTableGUI.popup.dismiss()
        self.refresh_table()

    def press_save(self, instance):
        self.friendInputGUI.save_in_database()
        self.refresh_table()


class BirthDayListApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        return BirthDayBaseGrid()


if __name__ == "__main__":
    app = BirthDayListApp()
    app.run()
