# libpack2gsm **[English](#english)**

Данный скрипт на Python выполняет конвертацию пакетов библиотек ArchiCAD версии 28 в контейнеры LCF, совместимые с ArchiCAD версии 25.

<img width="597" height="465" alt="изображение" src="https://github.com/user-attachments/assets/5e629ce5-6bf5-445b-9d64-2344cd13d3d6" />

## Описание
В ArchiCAD 28 изменился формат библиотек, что создает проблемы с обратной совместимостью для проектов, работающих в ArchiCAD 25-27. Данный скрипт преобразует пакеты из ArchiCAD 28 в формат LCF, который понимают ArchiCAD 25-27. При наличии русского перевода в libpack файлы LCF также будут переведены.

## Работа с программой

### Вариант 1 — использование графического интерфейса

1. Скачайте exe-файл из последнего релиза: https://github.com/kuvbur/libpack2gsm/releases/latest
2. Запустите программу и укажите необходимые параметры: пути к папкам, версии, язык
3. Начните конвертацию

При первом запуске будут загружены конвертеры LP_XMLConverter — этот процесс занимает некоторое время.

В ходе работы программа создает папку temp и папку tool. Папка temp удаляется после завершения конвертации.

### Вариант 2 — работа со скриптом напрямую

1. Клонируйте репозиторий или скачайте скрипт и папку tool (содержит конвертеры LP_XMLConverter версий 28 и 25)
2. В папке со скриптом создайте папки lcf и libpack
3. Скопируйте необходимые пакеты в папку libpack
4. Установите зависимости: pip install lxml
5. Запустите скрипт libpack2gsm.py

## Пример конвертации
https://disk.yandex.ru/d/KNtOiah8td9_hg

# English
libpack2gsm
This Python script converts ArchiCAD 28 library packages into LCF containers compatible with ArchiCAD 25.

## Description
In ArchiCAD 28, the library format has changed, creating backward compatibility issues for projects running in ArchiCAD 25-27. This script converts packages from ArchiCAD 28 into the LCF format understood by ArchiCAD 25-27. If a Russian translation is present in the libpack, the LCF files will also be translated.

## Working with the Program
### Option 1 — Using the Graphical Interface
1. Download the exe file from the latest release: https://github.com/kuvbur/libpack2gsm/releases/latest

2. Run the program and specify the required parameters: folder paths, versions, language

3. Start the conversion

On first launch, the LP_XMLConverter converters will be downloaded — this process takes some time.

During operation, the program creates a temp folder and a tool folder. The temp folder is deleted after conversion is complete.

### Option 2 — Working with the Script Directly
1. Clone the repository or download the script and the tool folder (contains LP_XMLConverter converters for versions 28 and 25)

2. In the script folder, create lcf and libpack folders

3. Copy the required packages into the libpack folder

4. Install dependencies: pip install lxml

5. Run the script libpack2gsm.py
