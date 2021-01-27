if __name__ == "__main__":
    print("Veuiller executer le script start_gui.py à la racine du projet")
    exit(1)
from tkinter import *
from tkinter import messagebox

import GUI.functions_gui as functions_gui
import GUI.main_tables as main_tables
import sys
import tkinter as tk
OPTIONS_ATT = ["ignore_field", "position_fields", "quid_cols", "sensitive_fields"]

class PrintLogger(): # create file like object
    def __init__(self, textbox, vsb): # pass reference to text widget
        self.textbox = textbox # keep ref
        self.vsb = vsb

    def write(self, text):
        self.textbox.insert(tk.END, text) # write text to textbox
        self.textbox.see("end")
            # could also scroll to end of textbox here to make sure always visible

    def flush(self): # needed for file like object
        pass



def openNewWindow():
    # créer la fenetre de paramètrage des attributs
    window2 = Toplevel(window)

    app_width = 800
    app_height = 800
    screen_width = globals()[f"window"].winfo_screenwidth()
    screen_height = globals()[f"window"].winfo_screenheight()

    x = (screen_width / 2) - (app_width / 2)
    y = (screen_height / 2) - (app_height / 2)

    # personnalisation de la fenetre
    window2.title("GDA Anonymization")
    window2.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
    window2.config(background='#41B79F')

    # Frame Pincipale
    frame2 = Frame(window2, bg='#41B79F')

    # Frame des labels
    frame_labels_att = Frame(frame2, bg='#41B79F')

    # Label "Message de bienvenue"
    label_title = Label(frame2, text="Paramétrage des attributs", font=("Helvetica", 15), bg="#41B79F", fg="white")
    label_title.pack()

    # Frame des labels
    frame_labels_att = Frame(frame2, bg='#41B79F', pady=10)

    # Création automatiques des colonnes avec les attributs
    list_attributs = functions_gui.getAttributs()
    x = 1

    # dictionnaire de résultats de l'attribut en cours => clé : attribut, valeurs : résultats
    valeurs_attributs = {}

    for att in list_attributs:

        globals()[f"label_{att}"] = Label(frame_labels_att, text=att + " : ", font=("Helvetica", 10), bg="#41B79F",
                                          fg="white")
        globals()[f"label_{att}"].grid(row=x, column=0, pady=5)

        OPTIONS_TYPE = ["INTEGER", "TEXT", "DATETIME", "DATE", "REAL"]
        globals()[f"set_type_{att}"] = StringVar()
        globals()[f"set_type_{att}"].set(OPTIONS_TYPE[1])
        set_type_drop = OptionMenu(frame_labels_att, globals()[f"set_type_{att}"], *OPTIONS_TYPE)
        set_type_drop.grid(row=x, column=1, padx=5)

        pos = 2
        for opt in OPTIONS_ATT:
            globals()[f"{att}-{opt}"] = IntVar()
            globals()[f"{att}-{opt}"].set(0)
            globals()[f"radioBT_{opt}"] = Checkbutton(frame_labels_att, text=opt, variable=(globals()[f"{att}-{opt}"])
                                                      , offvalue=0)
            # ,command=lambda: setValue())'''
            globals()[f"radioBT_{opt}"].grid(row=x, column=pos, padx=5)
            pos += 1
        x += 1

    def doStuff():
        getValues()
        loadingWindow()

    def getValues():
        for att in list_attributs:
            if att not in valeurs_attributs:
                valeurs_attributs[att] = []
            if len(valeurs_attributs[att]) >= 1:
                valeurs_attributs[att] = [globals()[f"set_type_{att}"].get()]
            else:
                valeurs_attributs[att].append(globals()[f"set_type_{att}"].get())
            for opt in OPTIONS_ATT:
                if globals()[f"{att}-{opt}"].get() == 1:
                    valeurs_attributs[att].append(opt)
        main_tables.processData(valeurs_attributs, OPTIONS_ATT)

    def loadingWindow():
        loading_window = Toplevel(window2)

        app_width = 400
        app_height = 400
        screen_width = globals()[f"window"].winfo_screenwidth()
        screen_height = globals()[f"window"].winfo_screenheight()

        x = (screen_width / 2) - (app_width / 2)
        y = (screen_height / 2) - (app_height / 2)

        # personnalisation de la fenetre
        loading_window.title("Etat de l'algorithme")
        loading_window.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
        loading_window.config(background='#41B79F')

        # label d'état
        state_label = Text(loading_window)
        vsb = tk.Scrollbar(orient="vertical", command=state_label.yview)
        state_label.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        state_label.pack(side="left", fill="both", expand=True)

        pl = PrintLogger(state_label, vsb)
        sys.stdout = pl

        loading_window.mainloop()

    # frame Boutton
    frame_SB2 = Frame(frame2, bg='#41B79F')

    # ajouter button
    button2 = Button(frame_SB2, text="Lancer l'anonymisation", font=("Helvetica", 15), bg="white", fg="#41B79F",
                     command=doStuff)
    button2.pack(pady=25, fill=X)

    '''state = StringVar()
    sys.stdout = state
    state_program = Entry(frame_SB2, text=state, font=("Helvetica", 10), bg="#41B79F", fg="white")
    state_program.pack(pady=25, fill=X)'''

    frame2.pack(expand=YES)
    frame_labels_att.pack(expand=YES)
    frame_SB2.pack(expand=YES)
    # affichage
    window2.mainloop()



def callFunction():
    tab_data = []
    # tab_data.append(entry_local_server_url.get())
    tab_data.append(entry_db_source_name.get())
    tab_data.append(entry_table_source_name.get())
    tab_data.append(entry_db_dest_name.get())
    tab_data.append(entry_table_dest_name.get())
    tab_data.append(entry_k_value.get())

    i = 0
    while i < len(tab_data):
        if tab_data[i] == '':
            messagebox.showerror(title="Erreur", message="Vous devez remplir tous les champs.")
            return None
        i += 1

    # dictionnaire de données
    tab_infos = {"local_server_url": entry_local_server_url.get(), "BD_source": entry_db_source_name.get(),
                 "Table_source": entry_table_source_name.get(), "BD_dest": entry_db_dest_name.get(),
                 "Table_dest": entry_table_dest_name.get(), "k_value": int(entry_k_value.get()),
                 "l_value": int(entry_l_value.get())}
    # "switch": switch_variable.get()}

    main_tables.getDatas(tab_infos)
    functions_gui.parametrageTable(tab_infos)

    openNewWindow()


# créer une premiere fenetre
window = Tk()

app_width = 300
app_height = 385
screen_width = globals()[f"window"].winfo_screenwidth()
screen_height = globals()[f"window"].winfo_screenheight()

x = (screen_width / 2) - (app_width / 2)
y = (screen_height / 2) - (app_height / 2)
# personnalisation de la fenetre
window.title("GDA Anonymization")

window.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
window.config(background='#41B79F')

screen_width = window.winfo_screenmmwidth()
screen_height = window.winfo_screenmmheight()

# Frame Pincipale
frame = Frame(window, bg='#41B79F')

# Frame des labels
frame_labels = Frame(frame, bg='#41B79F')

# Label "Message de bienvenue"
label_title = Label(frame, text="Paramètrages", font=("Helvetica", 15), bg="#41B79F", fg="white")
label_title.pack()

# Label "Local Server URL"
label_local_server_url = Label(frame_labels, text="Local Server URL : ", font=("Helvetica", 10), bg="#41B79F",
                               fg="white")
label_local_server_url.grid(row=0, column=0, pady=5)

# Input "Local Server URL"
# name_entry_local_server_url = StringVar()
entry_local_server_url = Entry(frame_labels, font=("Helvetica", 10), bg="#41B79F", fg="white")
entry_local_server_url.grid(row=0, column=1, pady=5)

# Label "BD Source name"
label_db_source_name = Label(frame_labels, text="BD Source name : ", font=("Helvetica", 10), bg="#41B79F", fg="white")
label_db_source_name.grid(row=1, column=0, pady=5)

# Input "BD Source name"
entry_db_source_name = Entry(frame_labels, font=("Helvetica", 10), bg="#41B79F", fg="white")
# POUR LES TESTS
entry_db_source_name.insert(0, "raw_banking")
entry_db_source_name.grid(row=1, column=1, pady=5)

# Label Table Source name"
label_table_source_name = Label(frame_labels, text="Table Source name : ", font=("Helvetica", 10), bg="#41B79F",
                                fg="white")
label_table_source_name.grid(row=2, column=0, pady=5)

# Input "Table Source name"
entry_table_source_name = Entry(frame_labels, font=("Helvetica", 10), bg="#41B79F", fg="white")
# POUR LES TESTS
entry_table_source_name.insert(0, "cards")
entry_table_source_name.grid(row=2, column=1, pady=5)

# Label BD Destination name"
label_db_dest_name = Label(frame_labels, text="BD Destination name : ", font=("Helvetica", 10), bg="#41B79F",
                           fg="white")
label_db_dest_name.grid(row=3, column=0, pady=5)

# Input "BD Destination name"
entry_db_dest_name = Entry(frame_labels, font=("Helvetica", 10), bg="#41B79F", fg="white")
# POUR LES TESTS
entry_db_dest_name.insert(0, "banking")
entry_db_dest_name.grid(row=3, column=1, pady=5)

# Label Table Destination name
label_table_dest_name = Label(frame_labels, text="Table Destination name : ", font=("Helvetica", 10), bg="#41B79F",
                              fg="white")
label_table_dest_name.grid(row=4, column=0, pady=5)

# Input "Table Destination name"
entry_table_dest_name = Entry(frame_labels, font=("Helvetica", 10), bg="#41B79F", fg="white")
# POUR LES TESTS
entry_table_dest_name.insert(0, "cards")
entry_table_dest_name.grid(row=4, column=1, pady=5)

# Label valeur de k
label_k_value = Label(frame_labels, text="Valeur de K : ", font=("Helvetica", 10), bg="#41B79F",
                      fg="white")
label_k_value.grid(row=6, column=0, pady=5)

# Input valeur de k
entry_k_value = Entry(frame_labels, font=("Helvetica", 10), bg="#41B79F", fg="white")
entry_k_value.grid(row=6, column=1, pady=5)

# Label valeur de l
label_l_value = Label(frame_labels, text="Valeur de L : ", font=("Helvetica", 10), bg="#41B79F",
                      fg="white")
label_l_value.grid(row=7, column=0, pady=5)

# Input valeur de l
entry_l_value = Entry(frame_labels, font=("Helvetica", 10), bg="#41B79F", fg="white")
entry_l_value.grid(row=7, column=1, pady=5)

'''# Switch GDA/Local
switch_frame = Frame(frame, bg='#41B79F', pady=5)

switch_variable = StringVar(value="off")
gda_button = Radiobutton(switch_frame, text="GDA", variable=switch_variable, indicatoron=False, value="gda", width=8)
local_button = Radiobutton(switch_frame, text="Local", variable=switch_variable, indicatoron=False, value="local",
                           width=8)
gda_button.pack(side="left", padx=5, fill=X)
local_button.pack(side="left", padx=5, fill=X)'''

# frame Boutton
frame_SB = Frame(frame, bg='#41B79F')

# ajouter button
button = Button(frame_SB, text="Valider mon choix", font=("Helvetica", 10), bg="white", fg="#41B79F",
                command=callFunction)
button.pack(pady=25, fill=X)

frame.pack(expand=YES)
frame_labels.pack(expand=YES)
'''switch_frame.pack(expand=YES)'''
frame_SB.pack(expand=YES)

# affichage
window.mainloop()
