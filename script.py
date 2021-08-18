import telebot
import pytesseract
import cv2
from PIL import Image
import json
import os

bot = telebot.TeleBot('1989270958:AAE8r0_syhZK07wpTk9PoUsTdOn4yC_AZiA')  # your bot token


@bot.message_handler(commands=['start'])
def help_command(message):
    bot.send_message(message.chat.id, "Пожалуйста отправьте фотографию документа")


def found_letters():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Student\AppData\Local\Tesseract-OCR\tesseract.exe'
    # получаем изоображение
    img = cv2.imread("images/1.png")
    image = Image.open('images/1.png')

    # получаем строку
    string = pytesseract.image_to_string(Image.open('images/1.png'), lang='rus')
    # печатаем
    alphabet2 = [chr(i) for i in range(ord("А"), ord("я") + 1)]
    # alphabet = [chr(i) for i in range(ord("A"), ord("Z") + 1)]
    cifri = [chr(i) for i in range(48, 58)]
    words = string.split()
    string = string.replace("\n", " ")
    newords = [chr(i) for i in range(32, 97) if chr(i) not in alphabet2 and chr(i) not in cifri]
    list1 = []
    (width, height) = image.size
    my_list = {
        "text": string,
        "tokens": [],
        "source": {
            "width": width,
            "height": height
        }
    }

    # чтобы нарисовать сделаем копию изображения
    # image_copy = img.copy()
    # получить все данные из изображения
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang='rus')

    # получить все вхождения нужного слова
    word_occurences = [i for i, word in enumerate(data["text"]) if word in words and word not in newords]

    for occ in word_occurences:
        # извлекаем ширину, высоту, верхнюю и левую позицию для обнаруженного слова
        bukva = data["text"][occ:occ + 1]
        bukva = ''.join(bukva)
        w = data["width"][occ]
        h = data["height"][occ]
        l = data["left"][occ]
        t = data["top"][occ]
        m = dict(text=bukva, position=dict(left=l, top=t, width=w, height=h), offset=occ)
        list1.append(m)
        # определяем все точки окружающей рамки
        # p1 = (l, t)
        # p2 = (l + w, t)
        # p3 = (l + w, t + h)
        # p4 = (l, t + h)
        # рисуем 4 линии (прямоугольник)
        # image_copy = cv2.line(image_copy, p1, p2, color=(255, 0, 0), thickness=2)
        # image_copy = cv2.line(image_copy, p2, p3, color=(255, 0, 0), thickness=2)
        # image_copy = cv2.line(image_copy, p3, p4, color=(255, 0, 0), thickness=2)
        # image_copy = cv2.line(image_copy, p4, p1, color=(255, 0, 0), thickness=2)
    my_list['tokens'].append(list1)

    # plt.imsave("gooo.png", image_copy)
    # plt.imshow(image_copy)
    # plt.show()
    print(my_list)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(my_list, f, ensure_ascii=False, indent=4)
    return 0


@bot.message_handler(content_types=['photo'])
def photo(message):
    chat_id = message.chat.id

    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)

    src = 'C:/Users/Student/PycharmProjects/pythonProject/images/' + file_info.file_path[7:]  # change to your diretory
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    new_file.close()
    if sum(os.path.isfile(os.path.join("images", f)) for f in os.listdir("images")) > 1:
        os.remove('images/1.png')
    dir = 'images'
    i = 1
    ext = "png"
    for file in os.listdir(dir):
        os.rename(f'{dir}/{file}', f'{dir}/{i}.{ext}')
        i = i + 1
    bot.reply_to(message, "Обробатываю фотографию...")
    found_letters()
    doc = open('data.json', 'rb')
    bot.send_document(message.chat.id, doc)
    bot.send_document(message.chat.id, "FILEID")


@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):
    try:
        chat_id = message.chat.id

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src = 'C:/Users/Student/PycharmProjects/pythonProject/images/' + message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        new_file.close()
        if sum(os.path.isfile(os.path.join("images", f)) for f in os.listdir("images")) > 1:
            os.remove('images/1.png')
        dir = 'images'
        i = 1
        ext = "png"
        for file in os.listdir(dir):
            os.rename(f'{dir}/{file}', f'{dir}/{i}.{ext}')
            i = i + 1
        bot.reply_to(message, "Секунду, обробатываю файл..")
        found_letters()
        doc = open('data.json', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_document(message.chat.id, "FILEID")
    except Exception as e:
        bot.reply_to(message, e)
    except Exception:
        bot.reply_to(message, "Упс, что-то пошло не так, попробуйте еще раз")


bot.polling(True)
