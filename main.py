from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivymd.uix.datatables import MDDataTable
from kivymd.app import MDApp
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.config import Config
from kivy.core.window import Window
import datetime
from KivyMD.kivymd.uix.button import MDFlatButton, MDRaisedButton
from KivyMD.kivymd.uix.dialog import MDDialog
from database import DataBase
from CostumeMDDatePecker import CostumeMDDatePicker


class DataBaseAdapter:
    def __init__(self, db_file=None):
        self.database = DataBase(db_file)

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
    def __init__(self, friends):
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
        self.dialog = None
        self.sorted_on = "Birthday"
        self.sorted_order = "ASC"
        self.elevation = 2
        self.popup = None
        self.remove_button = Button(text="REMOVE", background_color=[.69, .07, 0, 1],
                                    background_normal='')
        self.edit_button = Button(text="EDIT", background_color=[.25, .59, .76, 1],
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
                if int(month) <= current_month:
                    if int(day) <= current_day:
                        lower_date.append(row)
                        continue
                upper_date.append(row)
            except ValueError:
                pass
        rows_data = upper_date + lower_date
        return rows_data

    def action_on_row_press(self, instance_table, instance_row):
        result = list()

        for row_on_page in self.table_data.recycle_data:
            if str(row_on_page['Index']) == str(instance_row.index):
                result = list(filter(lambda x: x['range'] == row_on_page['range'], self.table_data.recycle_data))
                break

        layout = BoxLayout(orientation='horizontal', spacing=5, padding=5)
        self.remove_button.first_name = result[1]['text']
        self.remove_button.last_name = result[2]['text']
        self.remove_button.birth_date = result[3]['text']
        self.edit_button.first_name = result[1]['text']
        self.edit_button.last_name = result[2]['text']
        self.edit_button.birth_date = result[3]['text']

        layout.add_widget(self.remove_button)
        layout.add_widget(self.edit_button)

        self.popup = Popup(title='Row settings', content=layout, size_hint=(None, None), size=(220, 120))
        self.popup.open()


class MyGrid(Widget):
    gl_person_input = ObjectProperty(None)
    al_persons_info = ObjectProperty(None)
    gl_persons_scroll_info = ObjectProperty(None)
    first_name_input = ObjectProperty(None)
    last_name_input = ObjectProperty(None)
    birthday_input = ObjectProperty(None)
    button_save = ObjectProperty(None)
    hidden_id = ObjectProperty(None)
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database_adapter = DataBaseAdapter()
        Window.size = (1300, 500)
        self.friendTableGUI = FriendTableGUI(self.database_adapter.select_all_friends())
        self.all_bind()

    def remove_row(self, instance):
        data_list = [instance.first_name, instance.last_name, instance.birth_date]
        self.database_adapter.delete_friend_by_all_fields(data_list)
        self.friendTableGUI.popup.dismiss()
        self.refresh_table()

    def edit_row(self, instance):
        data_list = [instance.first_name, instance.last_name, instance.birth_date]
        self.first_name_input.text = instance.first_name
        self.last_name_input.text = instance.last_name
        self.birthday_input.text = instance.birth_date
        friend = self.database_adapter.find_one_by_all_fields(data_list)
        self.hidden_id.text = str(friend[0][0])
        self.friendTableGUI.popup.dismiss()
        self.refresh_table()

    def all_bind(self):
        self.friendTableGUI.remove_button = Button(text="REMOVE", on_press=self.remove_row,
                                                   background_color=[.69, .07, 0, 1],
                                                   background_normal='')
        self.friendTableGUI.edit_button = Button(text="EDIT", on_press=self.edit_row,
                                                 background_color=[.25, .59, .76, 1],
                                                 background_normal='')
        self.button_save.bind(on_press=self.save_in_database)
        self.birthday_input.bind(focus=self.birtday_input)
        self.al_persons_info.add_widget(self.friendTableGUI)

    def refresh_table(self):
        self.al_persons_info.remove_widget(self.friendTableGUI)
        self.friendTableGUI = FriendTableGUI(self.database_adapter.select_all_friends())
        self.friendTableGUI.remove_button = Button(text="REMOVE", on_press=self.remove_row,
                                                   background_color=[.69, .07, 0, 1],
                                                   background_normal='')
        self.friendTableGUI.edit_button = Button(text="EDIT", on_press=self.edit_row,
                                                 background_color=[.25, .59, .76, 1],
                                                 background_normal='')
        self.al_persons_info.add_widget(self.friendTableGUI)

    def save_in_database(self, instance):
        data_list = [self.first_name_input.text, self.last_name_input.text, self.birthday_input.text]
        if self.hidden_id.text:
            self.database_adapter.update_friend_by_id(data_list, self.hidden_id.text)
            self.hidden_id.text = ""
        else:
            self.database_adapter.insert_friend(data_list)
        self.refresh_table()
        self.first_name_input.text = ""
        self.last_name_input.text = ""
        self.birthday_input.text = ""

    def birtday_input(self, instance, value):
        if value:
            self.show_date_picker()

    def show_date_picker(self):
        picker = CostumeMDDatePicker(callback=self.got_date)
        picker.open()

    def got_date(self, the_date):
        try:
            self.birthday_input.text = str(the_date)
        except:
            pass


class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        return MyGrid()


if __name__ == "__main__":
    MyApp().run()
