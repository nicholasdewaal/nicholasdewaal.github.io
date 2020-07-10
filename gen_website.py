
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


def add_line(in_file, line):
    with open(in_file, 'a') as file:
        file.write('\n' + line)


def fetch_png_list(in_path):
    image_list = [x for x in os.listdir(in_path) if x[-3:] == "png"]
    image_list.sort()
    return image_list


def remove_if_exists(in_file):
    if os.path.exists(in_file):
        os.remove(in_file)


def make_dir(in_path):
    try:
        os.mkdir(in_path)
    except FileExistsError:
        pass


def gen_plot(df_in, save_path):
    if df_in.shape[0] > 80: # must have at least 80 cases to be worth it
        df_bars = df_in.groupby([df_in.FECHA_RESULTADO]).size()
        #df_bars = df_bars[df_bars.index > datetime.datetime(2020, 6, 15)]
        df_avg = df_bars.rolling(7).mean()
        df_avg.name = "Por medio de los 7 dias anteriores"
        fig, ax = plt.subplots()
        plt.xlabel("Fecha")
        plt.ylabel("Casos Nuevos Detectados")
        ax.bar(df_bars.index, df_bars.values)
        df_avg.plot(ax=ax, color="green", title="Casos Nuevos Detectados en " + save_path, legend=True)
        plt.tight_layout()
        x_axis = ax.axes.get_xaxis()
        y_axis = ax.axes.get_yaxis()
        x_label = x_axis.get_label()
        y_label = y_axis.get_label()
        x_label.set_visible(False)
        y_label.set_visible(False)
        plt.savefig(save_path + ".png", dpi=120)
        plt.clf()


df_pos = pd.read_csv("positivos_covid.csv", encoding = "ISO-8859-1")
#df_dead = pd.read_csv("fallecidos_covid.csv", encoding = "ISO-8859-1")

df_pos['FECHA_RESULTADO'] = pd.to_datetime(df_pos['FECHA_RESULTADO'], format="%d/%m/%Y")

df_pos.DISTRITO = df_pos.DISTRITO.str.replace('Ñ', 'N')
df_pos.PROVINCIA = df_pos.PROVINCIA.str.replace('Ñ', 'N')

df_pos.DISTRITO = df_pos.DISTRITO.str.replace('.', '')
df_pos.PROVINCIA = df_pos.PROVINCIA.str.replace('.', '')

df_pos.DISTRITO = df_pos.DISTRITO.str.replace('Ó', 'O')
df_pos.PROVINCIA = df_pos.PROVINCIA.str.replace('Ó', 'O')


try:
    arg = sys.argv[1]
except:
    pass

if arg == "noimages":
    all_departments = list()
else:
    all_departments = list(df_pos.DEPARTAMENTO.unique())

total_cases = dict()  # total cases by district

# Department > Provinces > Districts
# Generate and save all plots
for department in all_departments:
    make_dir(department)
    df_department = df_pos[df_pos.DEPARTAMENTO == department]
    # place departments in parent folder with filename of department
    gen_plot(df_department, department)
    containing_provinces = list(df_department['PROVINCIA'].unique())
    for province in containing_provinces:
        # place provinces in department folder, with filename of province, also making folder with province name
        save_path = department + '/' + province
        make_dir(save_path)
        df_province = df_department[df_department.PROVINCIA == province]
        gen_plot(df_province, save_path)
        containing_districts = list(df_province['DISTRITO'].unique())
        for district in containing_districts:
            # place districts in department/province folder
            save_path = department + '/' + province + '/' + district
            df_district = df_province[df_province.DISTRITO == district]
            total_cases[district] = df_district.shape[0]
            gen_plot(df_district, save_path)


all_departments = next(os.walk("."))[1]

for department in all_departments:
    department_link = department + '/' + department + '.html'
    remove_if_exists(department_link)
    os.mknod(department_link)
    department_images = fetch_png_list(department)

    add_line(department_link, "<html>\n    <head>\n    </head>\n    <body>")
    add_line(department_link, "<h1>Casos de COVID-19 en " + department + " por Provincia</h1>")
    add_line(department_link, "<h2>\n    Selecciona la foto de una Provincia para ver sus detalles por Distrito.\n</h2>")
    add_line(department_link, "<h3>\n    <a href=../index.html>Regresar a casos por Departamento</a>\n</h3>")

    for image in department_images:
        if image[-3:] == "png" and image[:6] != "EN INV":
            add_line(department_link, '        <a href="' + image[:-4] + '/'  + image[:-3] + 'html">')
            add_line(department_link, '            <img src="' + image + '">')
            add_line(department_link, r'        </a>')

    add_line(department_link, "    </body>")
    add_line(department_link, "</html>")

    all_provinces = next(os.walk(department))[1]
    for province in all_provinces:
        if len(os.listdir(department + '/' + province)) != 0:
            province_link = department + '/' + province + '/' + province + '.html'
            remove_if_exists(province_link)
            os.mknod(province_link)
            province_images = fetch_png_list(department + '/' + province)
            add_line(province_link, "<html>\n    <head>\n    </head>\n    <body>")
            add_line(province_link, "<h1>Casos de COVID-19 en " + department +" / " + province + " por Distrito</h1>")
            add_line(province_link, "<h3>\n    <a href=../../index.html>Regresar a casos por Departamento</a>\n</h3>")
            for image in province_images:
                if image[-3:] == "png" and image[:6] != "EN INV":
                    add_line(province_link, '        <img src="' + image + '">')

            add_line(province_link, "</body>")
            add_line(province_link, "</html>")
