import datetime
import sqlite3
import re
import PySimpleGUI as sg

sg.theme('LightGrey1')

conn = sqlite3.connect('reservations.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Hotels (
    Hotel_ID INTEGER PRIMARY KEY,
    Name TEXT,
    Address TEXT,
    Phone TEXT,
    Email TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS RoomTypes (
    Room_Type_ID INTEGER PRIMARY KEY,
    Name TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Reservations (
    Reservation_ID INTEGER PRIMARY KEY,
    Hotel_ID INTEGER,
    Room_Type_ID INTEGER,
    Check_In_Date DATE,
    Check_Out_Date DATE,
    Client_ID INTEGER,
    FOREIGN KEY (Hotel_ID) REFERENCES Hotels(Hotel_ID),
    FOREIGN KEY (Room_Type_ID) REFERENCES RoomTypes(Room_Type_ID),
    FOREIGN KEY (Client_ID) REFERENCES Clients(Client_ID)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Clients (
    Client_ID INTEGER PRIMARY KEY,
    First_Name TEXT,
    Last_Name TEXT,
    Phone TEXT,
    Email TEXT
)
''')

hotels_data = [
    ('Royal Hotel West', 'West Address', '12345678', 'west@example.com'),
    ('Royal Hotel East', 'East Address', '87654321', 'east@example.com'),
    ('Royal Hotel North', 'North Address', '98765432', 'north@example.com'),
    ('Royal Hotel South', 'South Address', '23456789', 'south@example.com')
]

room_types_data = [
    'Single', 'Double', 'Deluxe Room', 'Studio Room', 'King Room',
    'Presidential Suite'
]

for hotel_data in hotels_data:
  cursor.execute('SELECT * FROM Hotels WHERE Name=?', (hotel_data[0], ))
  if not cursor.fetchone():
    cursor.execute(
        'INSERT INTO Hotels (Name, Address, Phone, Email) VALUES (?, ?, ?, ?)',
        hotel_data)

for room_type in room_types_data:
  cursor.execute('SELECT * FROM RoomTypes WHERE Name=?', (room_type, ))
  if not cursor.fetchone():
    cursor.execute('INSERT INTO RoomTypes (Name) VALUES (?)', (room_type, ))

cursor.execute("SELECT * FROM Clients")
myresult = cursor.fetchall()

conn.commit()


def check_name(name):
  return bool(re.match("^[a-zA-Z]+$", name))


def check_phone(phone):
  return bool(re.match("^[0-9]+$", phone))


def check_email(email):
  return bool(re.match("[^@]+@[^@]+\.[^@]+", email))


def check_admin_password(password):
  return password == 'vika'


layout = [
    [
        sg.Text('Viesnīcu rezervācija',
                font=('Helvetica', 20),
                justification='center')
    ],
    [
        sg.Text('Izvēlieties viesnīcu un rezervējiet numuru',
                font=('Helvetica', 14),
                justification='center')
    ],
    [
        sg.Text('Viesnīca:', size=(15, 1)),
        sg.InputCombo([
            'Royal Hotel West', 'Royal Hotel East', 'Royal Hotel North',
            'Royal Hotel South'
        ],
                      key='hotel',
                      size=(20, 1))
    ],
    [
        sg.Text('Numurs:', size=(15, 1)),
        sg.InputCombo([
            'Single', 'Double', 'Deluxe Room', 'Studio Room', 'King Room',
            'Presidential Suite'
        ],
                      key='room',
                      size=(20, 1))
    ],
    [
        sg.Text('Ierašanās datums:', size=(15, 1)),
        sg.Input(key='cal_checkin',
                 enable_events=True,
                 readonly=True,
                 size=(10, 1)),
        sg.CalendarButton('Izvēlēties',
                          target='cal_checkin',
                          key='cal_checkin_button')
    ],
    [
        sg.Text('Izrakstīšanās datums:', size=(15, 1)),
        sg.Input(key='cal_checkout',
                 enable_events=True,
                 readonly=True,
                 size=(10, 1)),
        sg.CalendarButton('Izvēlēties',
                          target='cal_checkout',
                          key='cal_checkout_button')
    ],
    [
        sg.Text('Vārds:', size=(15, 1)),
        sg.Input(key='first_name', size=(20, 1))
    ],
    [
        sg.Text('Uzvārds:', size=(15, 1)),
        sg.Input(key='last_name', size=(20, 1))
    ],
    [
        sg.Text('Telefona numurs:', size=(15, 1)),
        sg.Input(key='phone', size=(20, 1))
    ],
    [
        sg.Text('E-pasta adrese:', size=(15, 1)),
        sg.Input(key='email', size=(20, 1))
    ],
    [sg.Button('Rezervēt', size=(20, 1))],
    [sg.Button('Izdzēst rezervāciju', size=(20, 1))],
    [
        sg.Button('Apskatīt visu rezervāciju informāciju',
                  size=(30, 1),
                  key='show_reservations')
    ],
    [
        sg.Button('Apskatīt informāciju par visam viesnīcām',
                  size=(30, 1),
                  key='show_hotel_info')
    ],
]

window = sg.Window('Viesnīcu rezervācija', layout, resizable=True)

while True:
  event, values = window.read()

  if event == sg.WIN_CLOSED:
    break

  if event == 'Rezervēt':
    hotel_name = values['hotel']
    room_type = values['room']
    checkin_date = values['cal_checkin']
    checkout_date = values['cal_checkout']
    first_name = values['first_name']
    last_name = values['last_name']
    phone = values['phone']
    email = values['email']

    try:
      if hotel_name and room_type and checkin_date and checkout_date and first_name and last_name and phone and email:
        checkin_date = datetime.datetime.strptime(checkin_date[:10],
                                                  '%Y-%m-%d').date()
        checkout_date = datetime.datetime.strptime(checkout_date[:10],
                                                   '%Y-%m-%d').date()

        if checkout_date <= checkin_date:
          raise ValueError(
              "Izrakstīšanās datums ir jābūt pēc ierašanās datuma.")

        if not check_name(first_name) or not check_name(last_name):
          raise ValueError(
              "Nederīgs vārda vai uzvārda formāts. Var saturēt tikai burtus.")

        if not check_phone(phone):
          raise ValueError(
              "Nederīgs telefona numura formāts. Var saturēt tikai ciparus.")

        if not check_email(email):
          raise ValueError("Nederīgs e-pasta adrese.")

        cursor.execute(
            '''
                            INSERT INTO Reservations (Hotel_ID, Room_Type_ID, Check_In_Date, Check_Out_Date, Client_ID) 
                            VALUES ((SELECT Hotel_ID FROM Hotels WHERE Name=?), 
                                    (SELECT Room_Type_ID FROM RoomTypes WHERE Name=?), ?, ?, 
                                    (SELECT COALESCE(MAX(Client_ID), 0) + 1 FROM Clients))
                            ''',
            (hotel_name, room_type, checkin_date, checkout_date))

        cursor.execute(
            '''
                            INSERT INTO Clients (First_Name, Last_Name, Phone, Email) 
                            VALUES (?, ?, ?, ?)
                            ''', (first_name, last_name, phone, email))

        conn.commit()

        sg.popup(f'Rezervācija ir veiksmīgi izveidota!\n'
                 f'Viesnīca: {hotel_name}\n'
                 f'Numura tips: {room_type}\n'
                 f'Ierašanās datums: {checkin_date}\n'
                 f'Izrakstīšanās datums: {checkout_date}\n'
                 f'Vārds: {first_name}\n'
                 f'Uzvārds: {last_name}\n'
                 f'Telefona numurs: {phone}\n'
                 f'E-pasta adrese: {email}')
      else:
        sg.popup('Lūdzu, aizpildiet visus laukus!')
    except ValueError as ve:
      sg.popup(f"Nederīgs datuma formāts: {ve}")
      continue

  if event == 'cal_checkin_button':
    date = sg.popup_get_date('Izvēlieties ierašanās datumu')
    if date:
      window['cal_checkin'].update(date.strftime('%Y-%m-%d'))

  if event == 'cal_checkout_button':
    date = sg.popup_get_date('Izvēlieties izrakstīšanās datumu')
    if date:
      window['cal_checkout'].update(date.strftime('%Y-%m-%d'))

  if event == 'Izdzēst rezervāciju':
    window.hide()
    admin_password = sg.popup_get_text('Ievadiet admin paroli:',
                                       password_char='*',
                                       title='Admin Parole')
    if admin_password is None:
      window.un_hide()
    elif check_admin_password(admin_password):
      cursor.execute(
          '''SELECT Reservations.Reservation_ID, Hotels.Name AS Hotel, RoomTypes.Name AS Room_Type, 
                                         Reservations.Check_In_Date, Reservations.Check_Out_Date, 
                                         Clients.First_Name, Clients.Last_Name, Clients.Phone, Clients.Email 
                                  FROM Reservations 
                                  INNER JOIN Hotels ON Reservations.Hotel_ID = Hotels.Hotel_ID 
                                  INNER JOIN RoomTypes ON Reservations.Room_Type_ID = RoomTypes.Room_Type_ID 
                                  INNER JOIN Clients ON Reservations.Client_ID = Clients.Client_ID'''
      )
      reservations = cursor.fetchall()
      layout_delete = [[
          sg.Text('Izvēlieties rezervāciju, kuru vēlaties izdzēst:',
                  font=('Helvetica', 14),
                  justification='center')
      ],
                       [
                           sg.Listbox(values=reservations,
                                      size=(80, 10),
                                      key='-RESERVATIONS-',
                                      enable_events=True)
                       ], [sg.Button('Dzēst', size=(20, 1))],
                       [sg.Button('Atcelt', size=(20, 1))]]
      window_delete = sg.Window('Izdzēst rezervāciju',
                                layout_delete,
                                resizable=True)

      while True:
        event_delete, values_delete = window_delete.read()

        if event_delete == sg.WIN_CLOSED or event_delete == 'Atcelt':
          window_delete.close()
          window.un_hide()
          break

        if event_delete == 'Dzēst':
          selected_reservation = values_delete['-RESERVATIONS-']
          if selected_reservation:
            reservation_id = selected_reservation[0][0]
            cursor.execute("DELETE FROM Reservations WHERE Reservation_ID=?",
                           (reservation_id, ))
            conn.commit()
            sg.popup(
                f"Rezervācija ar ID {reservation_id} ir veiksmīgi izdzēsta!")
            window_delete.close()
            window.un_hide()
            break
    else:
      sg.popup("Nepareiza admin parole!")
      window.un_hide()

  if event == 'show_reservations':
    window.hide()
    admin_password = sg.popup_get_text('Ievadiet admin paroli:',
                                       password_char='*',
                                       title='Admin Parole')
    if admin_password is None:
      window.un_hide()
    elif check_admin_password(admin_password):
      cursor.execute(
          '''SELECT Reservations.Reservation_ID, Hotels.Name AS Hotel, RoomTypes.Name AS Room_Type, 
                                         Reservations.Check_In_Date, Reservations.Check_Out_Date, 
                                         Clients.First_Name, Clients.Last_Name, Clients.Phone, Clients.Email 
                                  FROM Reservations 
                                  INNER JOIN Hotels ON Reservations.Hotel_ID = Hotels.Hotel_ID 
                                  INNER JOIN RoomTypes ON Reservations.Room_Type_ID = RoomTypes.Room_Type_ID 
                                  INNER JOIN Clients ON Reservations.Client_ID = Clients.Client_ID'''
      )
      reservations = cursor.fetchall()
      for reservation in reservations:
        print(f"Rezervācija ID: {reservation[0]}\n"
              f"Viesnīca: {reservation[1]}\n"
              f"Numura tips: {reservation[2]}\n"
              f"Ierašanās datums: {reservation[3]}\n"
              f"Izrakstīšanās datums: {reservation[4]}\n"
              f"Vārds: {reservation[5]}\n"
              f"Uzvārds: {reservation[6]}\n"
              f"Telefona numurs: {reservation[7]}\n"
              f"E-pasta adrese: {reservation[8]}\n"
              f"{'-'*30}")
      window.un_hide()
    else:
      sg.popup("Nepareiza admin parole!")
      window.un_hide()

  if event == 'show_hotel_info':
    cursor.execute('''SELECT * FROM Hotels''')
    hotels = cursor.fetchall()
    for hotel in hotels:
      print(hotel)

window.close()
conn.close()
