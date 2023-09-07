import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import io
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


image_labels = []  # Lista para almacenar las etiquetas de imágenes
title_labels = []  # Lista para almacenar las etiquetas de títulos


def clear_results():

    # Eliminar el lienzo y los marcos
    canvas.destroy()
    titles_frame.destroy()
    images_frame.destroy()


def perform_scraping():

    images = []
    titles = []

    search_term = search_entry.get()
    url = f"https://listado.mercadolibre.com.ar/{search_term.replace(' ', '%20')}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Configurar el modo headless
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "ui-search-layout__item"))
        )
    except Exception as e:
        print("Error waiting for page to load:", e)
        driver.quit()
        return

    product_cards = driver.find_elements(
        By.CLASS_NAME, "ui-search-layout__item")

    for product_card in product_cards:
        try:
            image_element = product_card.find_element(
                By.CSS_SELECTOR, ".ui-search-result-image__element")
            image_data = image_element.get_attribute("src")

            driver.execute_script(
                "arguments[0].scrollIntoView();", image_element)

            WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".ui-search-result-image__element")))

            image_data = image_element.get_attribute("src")
            image = Image.open(io.BytesIO(requests.get(image_data).content))

            if image_data:
                images.append(image)
                print("Image URL:", image_data)

            title = product_card.find_element(
                By.CLASS_NAME, "ui-search-item__title").text
            titles.append(title)
        except Exception as e:
            print("Error extracting data:", e)

    driver.quit()

    for image, title in zip(images, titles):
        try:
            image_label = tk.Label(root)
            image_label.image = ImageTk.PhotoImage(image)
            image_label.config(image=image_label.image)
            image_label.pack()

            title_label = tk.Label(root, text=title)
            title_label.pack()
        except Exception as e:
            print("Error displaying data:", e)


def clear_button_clicked():
    clear_results()


root = tk.Tk()
root.title("Web Scraping App")

# Cuadro de entrada y botón de búsqueda
search_frame = tk.Frame(root, bg="#f2f2f2", padx=10, pady=10)
search_label = tk.Label(search_frame, text="Enter search term:", bg="#f2f2f2")
search_label.pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT)
search_button = tk.Button(search_frame, text="Search",
                          command=perform_scraping, bg="#4CAF50", fg="white")
search_button.pack(side=tk.LEFT)
search_frame.pack(fill=tk.X)

# Crear un lienzo para desplazamiento
canvas = tk.Canvas(root)


# Crear marcos para títulos e imágenes
titles_frame = tk.Frame(canvas)
images_frame = tk.Frame(canvas)

# Colocar los marcos en el lienzo
canvas.create_window((0, 0), window=titles_frame, anchor="nw")
canvas.create_window((0, titles_frame.winfo_height()),
                     window=images_frame, anchor="nw")

# Configurar el desplazamiento
canvas.configure(scrollregion=canvas.bbox("all"))

root.mainloop()
