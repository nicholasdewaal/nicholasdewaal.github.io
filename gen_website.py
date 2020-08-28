
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#from ipdb import set_trace

attribution = '    </br> Fuente de los datos utilizados: <a href="https://www.datosabiertos.gob.pe/dataset/casos-positivos-por-covid-19-ministerio-de-salud-minsa"> Instituto Nacional de Salud y Centro Nacional de Epidemiologia, prevención y Control de Enfermedades – MINSA. </a>'
attribution += '\n    </br></br> <a href="https://cloud.minsa.gob.pe/apps/onlyoffice/s/XJ3NoG3WsxgF6H8?fileId=613439">Datos Demograficos Utilizado</a>'
attribution += '\n    </br></br> <a href="https://github.com/nicholasdewaal/nicholasdewaal.github.io/blob/master/gen_website.py">Fuente del codigo</a> usado para generar este sitio web.</br></br></br></br>'

# Some constants used for image names
danger_img_name = "_1peligro.png"
len_danger = len(danger_img_name)
casenum_img_nm = "_casos_total.png"
len_casenum = len(casenum_img_nm)


def add_line(in_file, line):
    with open(in_file, 'a') as file:
        file.write('\n' + line)


def titulo(in_str):
    '''
    turn a string into a Spanish title
    use title to make lower case non-beginning letters and make De de
    '''
    return in_str.title().replace("De", "de")


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
    '''
    Build and save plot for the number of cases as a bar plot along with its
    7-day average.
    df_in is a pandas dataframe with the number of cases by date
    save_path is the path to save the plot (string)
    '''
    if df_in.shape[0] > 20:
        df_bars = df_in.groupby([df_in.FECHA_RESULTADO]).size()

        # Zero fill missing dates
        min_date = df_bars.index.min()
        max_date = df_in.FECHA_RESULTADO.max()
        idx = pd.date_range(min_date, max_date)
        df_bars = df_bars.reindex(idx, fill_value=0)

        df_avg = df_bars.rolling(7).mean()
        df_avg.name = "Promedio de los 7 dias anteriores"
        fig, ax = plt.subplots()
        df_avg.plot(
            ax=ax,
            color="maroon",
            title="Casos Nuevos Detectados en " +
            titulo(save_path),
            legend=True)
        # set_trace()
        ax.bar(df_bars.index, df_bars.values,
               color="gray", width=np.timedelta64(1, 'D'))
        plt.tight_layout()
        x_axis = ax.axes.get_xaxis()
        x_label = x_axis.get_label()
        x_label.set_visible(False)
        plt.savefig(save_path + ".png", dpi=120)
        plt.clf()


def sort_dict(in_dict, reverse=False, multiply_factor=1):
    '''
    Sort in_dict by its values, and multiply values by multiply_factor
    '''
    return {k: round( v * multiply_factor, 1)
        for k, v in sorted(in_dict.items(), key=lambda item: item[1],
            reverse=reverse)}


def clr(in_num):
    '''
    Define color for plots based on ranges of new weekly covid-19 cases per
    100000 people in a region.
    Red means high risk, orange means medium risk, yellow medium-low, green
    otherwise.
    '''
    # 35 is about half of the peak of Spain's worst point during pandemic
    if in_num > 38:
        return "red"
    elif in_num > 28:
        return "orangered"
    elif in_num > 19:
        return "orange"
    elif in_num > 12:
        return "gold"
    elif in_num > 9:
        return "yellow"
    # 8 is the level in Germany during free movement
    elif in_num > 6:
        return "yellowgreen"
    return "green"


def bar_h_covid(in_plot_dict, figure_txt, save_path,
                limit_extremes=False, colorize=False):
    '''
    Horizontal bar plot of covid-19 cases per 100000 saved in save_path
    limit_extremes: set to True if you want to limit extremely long plot bars.
    colorize: set to True if you want to color bars by covid danger.
    '''
    plot_dict = sort_dict(in_plot_dict, multiply_factor=100000)
    width = 8  # width of plot
    num_bars = len(plot_dict)
    n_chars_plot = 16

    if num_bars > 0:
        plt.subplots(figsize=(width, num_bars / 6 + 2.9))
        # Limit max length of extreme values in bar plot to 5 times
        # average value size / bar length
        legend, values = zip(*plot_dict.items())
        legend = [titulo(x[:n_chars_plot]) for x in legend]
        if limit_extremes:
            # exclude zeros in average
            value_average = sum(values) / (len(values) - sum(1 for x in values
                                                             if x == 0))
            if max(values) / 2 > value_average:
                plot_limit = min(max(values), 3 * value_average)
                plt.xlim(0, plot_limit)

        plt.figtext(.5, .9, figure_txt, fontsize=13, ha='center')
        if colorize:
            plt.barh(legend, values, color=list(map(clr, values)))
            plt.xlabel(
                "Sospecho de peligro actual. Rojo es alto peligro, verde es leve.",
                fontsize=9)
        else:
            plt.barh(legend, values, color="lightskyblue")

        x_loc = max(values) / 20
        for index, value in enumerate(values):
            plt.text(x_loc, index, str(value), fontsize="x-small")
        plt.savefig(save_path)
        plt.close()


# Make dataframes from csv files.
df_pos = pd.read_csv("positivos_covid.csv", encoding="ISO-8859-1")
df_pop = pd.read_csv("PoblacionPeru2020.csv")

df_pos['FECHA_RESULTADO'] = pd.to_datetime(
    df_pos['FECHA_RESULTADO'], format="%Y%m%d")

# Get rid of characters that are inconvenient to deal with
df_pos.DISTRITO = df_pos.DISTRITO.str.replace('Ñ', 'N')
df_pos.PROVINCIA = df_pos.PROVINCIA.str.replace('Ñ', 'N')

df_pop.DISTRITO = df_pop.DISTRITO.str.replace('Ñ', 'N')
df_pop.PROVINCIA = df_pop.PROVINCIA.str.replace('Ñ', 'N')

df_pos.DISTRITO = df_pos.DISTRITO.str.replace('.', '')
df_pos.PROVINCIA = df_pos.PROVINCIA.str.replace('.', '')

df_pop.DISTRITO = df_pop.DISTRITO.str.replace('.', '')
df_pop.PROVINCIA = df_pop.PROVINCIA.str.replace('.', '')

df_pos.DISTRITO = df_pos.DISTRITO.str.replace('Ó', 'O')
df_pos.PROVINCIA = df_pos.PROVINCIA.str.replace('Ó', 'O')

df_pop.DISTRITO = df_pop.DISTRITO.str.replace('Ó', 'O')
df_pop.PROVINCIA = df_pop.PROVINCIA.str.replace('Ó', 'O')

# Uncomment the line below to only look at results for PCR tests
# df_pos = df_pos[df_pos.METODODX=="PCR"]

# Usually data that just came in is incomplete for the most recent day, so
# remove it.
mx_date = df_pos.FECHA_RESULTADO.max()
df_pos = df_pos[df_pos.FECHA_RESULTADO < mx_date]


try:
    arg = sys.argv[1]
except BaseException:
    arg = ""

if arg == "noimages":
    all_departments = list()
else:
    all_departments = list(df_pos.DEPARTAMENTO.unique())

total_cases = dict()  # total cases by district

gen_plot(df_pos, "Todo Peru")
# Department > Provinces > Districts
# Generate and save all case growth plots
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
    print("Finished plots for", department)

# -------------------------Create plots for per capita results------------

plt.rc('ytick', labelsize=7.5)  # set size of font on y-axis for bar plots
failed_districts = list()
all_departments = list(df_pop.DEPARTAMENTO.unique())

cases_text1 = 'Casos Nuevos en los Ultimos 7 Dias por 100,000 Habitantes'
cases_text2 = 'Total de Casos Historicos Detectados por 100,000 Habitantes'

# Do risk plots by Department
total_positive = dict()
dep_sizes = dict()
dep_risks = dict()

for dep in all_departments:
    if dep == "LIMA":
        df_dep = df_pos[df_pos.DEPARTAMENTO.isin(["LIMA REGION", "LIMA"])]
    else:
        df_dep = df_pos[df_pos.DEPARTAMENTO == dep]
    df_bars = df_dep.groupby([df_dep.FECHA_RESULTADO]).size()
    min_date = df_bars.index.min()
    max_date = df_pos.FECHA_RESULTADO.max()
    idx = pd.date_range(min_date, max_date)
    df_bars = df_bars.reindex(idx, fill_value=0)
    df_avg = df_bars.rolling(7).mean()
    # Population of a department
    dep_pop = df_pop[df_pop.DEPARTAMENTO == dep].Population.sum()
    # pct of total infections in a Department
    total_positive[dep] = df_dep.shape[0] / dep_pop
    dep_risks[dep] = df_avg[-1] / dep_pop

bar_h_covid(dep_risks, cases_text1 + "/Departamento",
            "Departamento" + danger_img_name, True, True)
bar_h_covid(total_positive, cases_text2 + "/Departamento",
            "Departamento" + casenum_img_nm)

if arg == "noimages":
    all_departments = list()
for department in all_departments:
    all_provinces = list(
        df_pop[df_pop.DEPARTAMENTO == department].PROVINCIA.unique())

    for province in all_provinces:
        districts = df_pop[df_pop.PROVINCIA == province].DISTRITO.unique()

        total_positive = dict()
        districts = sorted(districts)
        district_sizes = dict()  # population of a district
        district_risks = dict()  # risk level by district

        for district in districts:

            df_district = df_pos[df_pos.PROVINCIA == province][df_pos.DISTRITO == district]
            df_bars = df_district.groupby([df_district.FECHA_RESULTADO]).size()
            min_date = df_bars.index.min()
            max_date = df_pos.FECHA_RESULTADO.max()
            try:
                idx = pd.date_range(min_date, max_date)
                df_bars = df_bars.reindex(idx, fill_value=0)
            except BaseException:
                print("No times for ", district)
            df_avg = df_bars.rolling(7).mean()

            try:
                district_size = df_pop[df_pop.PROVINCIA == province][df_pop.DISTRITO == district].Population.values[0]
                factor = df_district.shape[0] / district_size
                if factor > 0:
                    district_sizes[district] = district_size
                    total_positive[district] = factor

                if district_sizes[district] > 0 and not(np.isnan(df_avg[-1])):
                    district_risk_factor = df_avg[-1] / district_sizes[district]
                    district_risks[district] = district_risk_factor

            except BaseException:
                failed_districts.append(
                    (district, df_pop[df_pop.PROVINCIA == province][df_pop.DISTRITO == district].Population.values[0]))

        print("Finished plots for", province, "province")

        try:
            cases_path1 = department + '/' + province + '/' + province + danger_img_name
            cases_path2 = department + '/' + province + '/' + province + casenum_img_nm
            bar_h_covid(district_risks, cases_text1, cases_path1, True, True)
            bar_h_covid(total_positive, cases_text2, cases_path2)
        except BaseException:  # when Lima region shows up
            cases_path1 = department + ' REGION/' + \
                province + '/' + province + danger_img_name
            cases_path2 = department + ' REGION/' + \
                province + '/' + province + casenum_img_nm
            bar_h_covid(district_risks, cases_text1, cases_path1, True, True)
            bar_h_covid(total_positive, cases_text2, cases_path2)


# -------------------------Create all html pages----------------------------

all_departments = next(os.walk("."))[1]

for department in all_departments:
    department_link = department + '/' + department + '.html'
    remove_if_exists(department_link)
    os.mknod(department_link)
    department_images = fetch_png_list(department)

    add_line(department_link, "<html>\n  <head>\n  </head>\n  <body>")
    add_line(
        department_link,
        "    <h1>Casos de COVID-19 en " + department + " por Provincia</h1>")
    add_line(
        department_link,
        "    <h2>Seleccione la foto de una Provincia para ver sus detalles por Distrito.</h2>")
    add_line(
        department_link,
        "    <h3>\n      <a href=../index.html>Regresar a casos por Departamento</a>\n    </h3>")

    for image in department_images:
        # Exclude generating html links of images of EN INVESTIGACION and those
        # that are not png files.
        if image[-3:] == "png" and image[:6] != "EN INV":
            # dist_image_num = len(os.listdir(department + '/' + province))
            # if dist_image_num > 0:
            add_line(department_link, '    <a href="' +
                     image[:-4] + '/' + image[:-3] + 'html">')
            add_line(department_link, '      <img src="' + image + '">')
            # if dist_image_num > 0:
            add_line(department_link, r'    </a>')

    add_line(department_link, attribution)
    add_line(department_link, "  </body>")
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
                "<html>\n  <head>\n  </head>\n  <body>")
            add_line(
                province_link,
                "    <h1>Casos de COVID-19 en " + department + " / " +
                province + " por Distrito</h1>")
            add_line(
                province_link,
                "    <h3>\n      <a href=../../index.html>Regresar a casos por Departamento</a>\n    </h3>")
            add_line(
                province_link,
                "    <h4>\n Tome en cuenta que es común tener casos reportados en un distrito donde personas no viven a veces causando resultados exageradamente alto o bajo y sesgos en los datos. Por eso, interprete los resultados como tendencias del distrito y sus distritos cercanos.\n    </h4>")
            for image in province_images:
                # Place summary images 1st.
                risk_image = (image[-len_casenum:] == casenum_img_nm or image[-len_danger:] == danger_img_name)
                if risk_image:
                    add_line(province_link, '    <img src="' + image + '">')
            for image in province_images:
                risk_image = (image[-len_casenum:] == casenum_img_nm or image[-len_danger:] == danger_img_name)
                if image[-3:] == "png" and image[:6] != "EN INV" and not(risk_image):
                    add_line(province_link, '    <img src="' + image + '">')

            add_line(province_link, attribution)
            add_line(province_link, "</body>\n</html>")
