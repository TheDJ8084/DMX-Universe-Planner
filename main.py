import PySimpleGUI as sg
import importlib
import csv

sg.theme("Black")

file_names = [
    "Universe1",
    "Universe2",
    "Universe3",
    "Universe4",
    "Universe5",
    "Universe6",
    "Universe7",
    "Universe8",
]


def load_data(module_name):
    try:
        module = importlib.import_module(module_name)
        return module.Addresses
    except Exception as e:
        print(f"Error loading data from {module_name}: {e}")
        return []


DMX_data = [load_data(module_name) for module_name in file_names]

headings = ["Address", "Fixture", "FID"]


def tab(i, data):
    return [
        [sg.Text(f"Universe {i + 1}")],
        [
            sg.Table(
                values=data,
                headings=headings,
                expand_x=True,
                expand_y=True,
                hide_vertical_scroll=True,
                num_rows=16,
                auto_size_columns=True,
                key=f"-TABLE-{i}-",
            )
        ],
    ]


index = len(file_names)

tabgroup = [
    [
        sg.Tab(f"Universe {i + 1}", tab(i, DMX_data[i]), key=f"Tab {i}")
        for i in range(index)
    ]
]

layout = [
    [sg.TabGroup(tabgroup, key="TabGroup")],
    [sg.Text(text="Fixture"), sg.Input(key="name")],
    [sg.Text(text="Amount"), sg.Input(key="amount")],
    [sg.Text(text="DMX channels"), sg.Input(key="channels")],
    [sg.Text(text="DMX Address"), sg.Input(key="dmx1")],
    [sg.Text(text="FID"), sg.Input(key="fid1")],
    [sg.Button("OK"), sg.Button("Export current universe")],
]

window = sg.Window(
    "DMX Universe Planner V0.0.1-alpha", layout, finalize=True, icon="icon.ico"
)
window["TabGroup"].bind("<<NotebookTabChanged>>", "+Switch")


def update_table(values, tab_index):
    window[f"-TABLE-{tab_index}-"].update(values=values)


def export_to_csv(filename, data):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["Address", "Fixture", "FID"])

        for entry in data:
            writer.writerow(entry)


while True:
    event, values = window.read()

    if event == "OK":
        try:
            start_index = int(values["dmx1"]) - 1
            channels = int(values["channels"])
            amount = int(values["amount"])
            end_index = start_index + (channels * amount)
            new_fixture_name = values["name"]
            fid1_value = int(values["fid1"])

            tab_index = int(values["TabGroup"].split(" ")[1])
            for i in range(start_index, end_index):
                DMX_data[tab_index][i][1] = new_fixture_name
                try:
                    existing_fid_value = int(DMX_data[tab_index][i][2])
                    DMX_data[tab_index][i][2] = str(existing_fid_value + fid1_value)
                except ValueError:
                    sg.popup_error(
                        f"The existing FID value at index {i} is not a number."
                    )

            update_table(DMX_data[tab_index], tab_index)
            for key in values:
                if key in ["name", "amount", "channels", "dmx1", "fid1"]:
                    window[key].update("")

        except ValueError:
            sg.popup_error(
                "Please enter valid numeric values for DMX Address, FID, Channels, and Amount."
            )

    if event == "Export":
        try:
            tab_index = int(values["TabGroup"].split(" ")[1])
            export_filename = f"Universe{tab_index + 1}_export.csv"
            export_to_csv(export_filename, DMX_data[tab_index])
            sg.popup(f"Data exported to {export_filename}")
        except Exception as e:
            sg.popup_error(f"Error exporting data: {e}")

    if event == sg.WIN_CLOSED or event == "Exit":
        break

window.close()
