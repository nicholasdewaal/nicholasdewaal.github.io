
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

attribution = '</br> Fuente de los datos utilizados: <a href="https://www.datosabiertos.gob.pe/dataset/casos-positivos-por-covid-19-ministerio-de-salud-minsa"> Instituto Nacional de Salud y Centro Nacional de Epidemiologia, prevención y Control de Enfermedades – MINSA. </a>'
attribution += '</br></br> <a href="https://cloud.minsa.gob.pe/apps/onlyoffice/s/XJ3NoG3WsxgF6H8?fileId=613439">Datos Demograficos de MINSA</a>'
attribution += '</br></br> <a href="https://github.com/nicholasdewaal/nicholasdewaal.github.io/blob/master/gen_website.py">Fuente del codigo</a> usado para generar este sitio web.</br></br></br></br>'


def add_line(in_file, line):
    with open(in_file, 'a') as file:
        file.write('\n' + line)


def fetch_png_list(in_path):
    image_list = sorted([x for x in os.listdir(in_path) if x[-3:] == "png"])
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
    if df_in.shape[0] > 20:
        df_bars = df_in.groupby([df_in.FECHA_RESULTADO]).size()
        #df_bars = df_bars[df_bars.index > datetime.datetime(2020, 6, 15)]
        df_avg = df_bars.rolling(7).mean()
        df_avg.name = "Por medio de los 7 dias anteriores"
        fig, ax = plt.subplots()
        # plt.xlabel("Fecha")
        # plt.ylabel("Casos Nuevos Detectados")
        df_avg.plot(
            ax=ax,
            color="green",
            title="Casos Nuevos Detectados en " +
            save_path,
            legend=True)
        ax.bar(df_bars.index, df_bars.values)
        plt.tight_layout()
        x_axis = ax.axes.get_xaxis()
        # y_axis = ax.axes.get_yaxis()
        x_label = x_axis.get_label()
        # y_label = y_axis.get_label()
        x_label.set_visible(False)
        # y_label.set_visible(False)
        plt.savefig(save_path + ".png", dpi=120)
        plt.clf()


def sort_dict(in_dict, reverse=False, multiply_factor=1):
    return {k: round(v * multiply_factor, 1) for k, v in sorted(in_dict.items(), key=lambda item: item[1], reverse=reverse)}


def clr(in_num):
    '''
    Define color based on ranges of numbers
    '''
    if in_num > 17:
        return "red"
    elif in_num > 10:
        return "orange"
    elif in_num > 5:
        return "yellow"
    return "green"


df_pos = pd.read_csv("positivos_covid.csv", encoding="ISO-8859-1")
#df_dead = pd.read_csv("fallecidos_covid.csv", encoding = "ISO-8859-1")
df_pop = pd.read_csv("PoblacionPeru2020.csv", encoding = "ISO-8859-1")

df_pos['FECHA_RESULTADO'] = pd.to_datetime(
    df_pos['FECHA_RESULTADO'], format="%Y%m%d")

df_pos.DISTRITO = df_pos.DISTRITO.str.replace('Ñ', 'N')
df_pos.PROVINCIA = df_pos.PROVINCIA.str.replace('Ñ', 'N')

df_pos.DISTRITO = df_pos.DISTRITO.str.replace('.', '')
df_pos.PROVINCIA = df_pos.PROVINCIA.str.replace('.', '')

df_pos.DISTRITO = df_pos.DISTRITO.str.replace('Ó', 'O')
df_pos.PROVINCIA = df_pos.PROVINCIA.str.replace('Ó', 'O')


try:
    arg = sys.argv[1]
except BaseException:
    arg = ""

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
        # place provinces in department folder, with filename of province, also
        # making folder with province name
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

#-------------------------Create plots for per capita results----------------------------

if arg == "noimages":
    all_departments = list()
else:
    all_departments = list(df_pop.DEPARTAMENTO.unique())

plt.rc('ytick', labelsize=7.5) # set size of font on y-axis for bar plots

failed_districts = list()

for department in all_departments:
    all_provinces = list(df_pop[df_pop.DEPARTAMENTO==department].PROVINCIA.unique())

    for province in all_provinces:
        districts = df_pop[df_pop.PROVINCIA==province].DISTRITO.unique()

        total_positive = dict()
        districts = list(districts)
        districts.sort()
        district_sizes = dict() # population of a district
        district_risks = dict() # risk level by district

        for district in districts:

            df_district = df_pos[df_pos.PROVINCIA==province][df_pos.DISTRITO==district]
            df_bars = df_district.groupby([df_district.FECHA_RESULTADO]).size()
            df_avg = df_bars.rolling(7).mean()

            try:
                district_size = df_pop[df_pop.PROVINCIA==province][df_pop.DISTRITO==district].Population.values[0]
                factor = df_district.shape[0] / district_size
                if factor > 0:
                    district_sizes[district] = district_size
                    total_positive[district] = factor

                if district_sizes[district] > 0 and not(np.isnan(df_avg[-1])):
                    district_risk_factor = df_avg[-1] / district_sizes[district]

                    #if np.isnan(district_risk_factor):
                     #   set_trace()
                    district_risks[district] = district_risk_factor
                    #set_trace()

            except:
                failed_districts.append((district, df_pop[df_pop.PROVINCIA==province][df_pop.DISTRITO==district].Population.values[0]))

        print(province, district_risks)
        plot_dict = sort_dict(district_risks, multiply_factor=100000)
        print('plot:', plot_dict)
        #if province == "HUAROCHIRI":
         #   set_trace()
        num_bars = len(plot_dict)
        width = 8
        if num_bars > 0:
            legend, values = zip(*plot_dict.items())
            legend = [x[:16].title().replace("De", "de") for x in legend]
            plt.subplots(figsize=(width, num_bars/6 + 1.7))

            if max(values) / 2 > sum(values) / len(values):
                plot_limit = min(max(values) / 2, 2.5 * sum(values) / len(values))
                plt.xlim(0, plot_limit)

            plt.figtext(.5,.9,'Positivos de Ultima Semana por 100,000 (Sospecho de Peligro Actual)', fontsize=14, ha='center')
            plt.barh(legend, values, color=list(map(clr, values)))
            try:
                plt.savefig(department + '/' + province + '/' + province + "_peligro.png")
                plt.close()

            except: # when Lima region shows up
                plt.savefig(department + ' REGION/' + province + '/' + province + "_peligro.png")
                plt.close()

        plot_dict2 = sort_dict(total_positive, multiply_factor=100000)
        num_bars = len(plot_dict2)
        if num_bars > 0:
            plt.subplots(figsize=(width, num_bars/6 + 1.7))
            legend, values = zip(*plot_dict2.items())
            legend = [x[:16].title().replace("De", "de") for x in legend]
            plt.figtext(.5,.9,'Total de Casos Historicos Detectados por 100,000 Personas', fontsize=14, ha='center')
            plt.barh(legend, values)
            try:
                plt.savefig(department + '/' + province + '/' + province + "_casos_total.png")
            except: # when Lima region shows up
                plt.savefig(department + ' REGION/' + province + '/' + province + "_casos_total.png")
            plt.close()


#-------------------------Create all html pages----------------------------

all_departments = next(os.walk("."))[1]

for department in all_departments:
    department_link = department + '/' + department + '.html'
    remove_if_exists(department_link)
    os.mknod(department_link)
    department_images = fetch_png_list(department)

    add_line(department_link, "<html>\n    <head>\n    </head>\n    <body>")
    add_line(
        department_link,
        "<h1>Casos de COVID-19 en " +
        department +
        " por Provincia</h1>")
    add_line(
        department_link,
        "<h2>\n    Seleccione la foto de una Provincia para ver sus detalles por Distrito.\n</h2>")
    add_line(
        department_link,
        "<h3>\n    <a href=../index.html>Regresar a casos por Departamento</a>\n</h3>")

    for image in department_images:
        # Exclude generating html links of images of EN INVESTIGACION and those
        # that are not png files.
        if image[-3:] == "png" and image[:6] != "EN INV":
            # dist_image_num = len(os.listdir(department + '/' + province))
            # if dist_image_num > 0:
            add_line(department_link, '        <a href="' +
                     image[:-4] + '/' + image[:-3] + 'html">')
            add_line(department_link, '            <img src="' + image + '">')
            # if dist_image_num > 0:
            add_line(department_link, r'        </a>')

    add_line(department_link, attribution)
    add_line(department_link, "    </body>")
    add_line(department_link, "</html>")

    all_provinces = next(os.walk(department))[1]
    for province in all_provinces:
        if len(os.listdir(department + '/' + province)) != 0:
            province_link = department + '/' + province + '/' + province + '.html'
            remove_if_exists(province_link)
            os.mknod(province_link)
            province_images = fetch_png_list(department + '/' + province)
            add_line(
                province_link,
                "<html>\n    <head>\n    </head>\n    <body>")
            add_line(
                province_link,
                "<h1>Casos de COVID-19 en " +
                department +
                " / " +
                province +
                " por Distrito</h1>")
            add_line(
                province_link,
                "<h3>\n    <a href=../../index.html>Regresar a casos por Departamento</a>\n</h3>")

            for image in province_images:
                risk_image = (image[-16:] == '_casos_total.png' or image[-12:] == '_peligro.png')
                if risk_image:
                    add_line(province_link, '        <img src="' + image + '">')
            for image in province_images:
                risk_image = (image[-16:] == '_casos_total.png' or image[-12:] == '_peligro.png')
                if image[-3:] == "png" and image[:6] != "EN INV" and not(risk_image):
                    add_line(
                        province_link,
                        '        <img src="' +
                        image +
                        '">')

            add_line(province_link, attribution)
            add_line(province_link, "</body>\n</html>")
