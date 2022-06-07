# Geocoder
###### Авторы: Машкин Михаил, Шкут Марк
###### Группа: ФТ-103
___
### Описание
Геокодер. На вход подается адрес в свободном формате.  
На выходе список всех подходящих объектов (полный адрес, координаты, индекс)
___
### Требования
Python>=3.x.x  
PyQt5~=5.15.6
___
### Как пользоваться
1. Установите модули из `requirements.txt`
2. Запустите `main.py`
3. Введите в поисковой строке адрес в формате _Город Улица Дом_
4. Нажмите **Найти** или **Enter**.
5. Выберите подходящий адрес двойным **ЛКМ** или нажав **Выбрать**
___
### Состав проекта
- `data` данные (см. построение базы)
- `tests`
  - `tests/parser_tests.py` тесты для `request_parsing.py`
  - `tests/database_tests.py` тесты для `database_scripts/DB.py`
- `database`
  - `database_scripts/DB.py` класс, описывающий абстрактную БД
  - `database_scripts/parameter.py` класс, описывающий параметра абстрактной БД
  - `database_scripts/param_name_list.py` класс, описывающий имена колонок абстрактной БД
  - `database_scripts/table.py` класс, описывающий таблицу абстрактной БД
-`gui`
  - `gui.py` скрипт логики графической оболочки
  - `geocoder.ui` PyQt файл gui приложения
- `app`
  - `__main__.py` скрипт запуска приложения (с gui)
  - `request_parsing.py` парсинг запросов пользователя
  - `company_finder.py` поиск организаций из результата request_parsing.py с yandex-search api
- `preprocessing.py` подготовка БД из сырых OSM данных
- `settings.py` все настройки проекта (пути, названия таблиц и пр.)
___
### Извлечение БД
1. С помощью утилиты `osmium` из `data/russia-latest.osm.pbf` 
(Сырые OSM данные России с https://download.geofabrik.de/russia.html)
выгружаются все nodes и ways, содержащие тэги `addr:city`, `addr:street` и `addr:housenumber`
в `data/addresses.osm.pbf`
2. Выгружаются все nodes, сожержащиеся в ways из `data/addresses.osm.pbf`
в `data/linked-nodes.osm.pbf` для вычисления координат.
3. `preprocessing.py`: С помощью библиотеки `pyosmium` из извлеченных данных создается основная таблица,
содержащая город, улицу, дом, ширину, долготу, индекс (если указан `addr:postcode`).
4. Из основной таблицы создаются две спомогательные (города и улицы) для оптимизации поиска
___
### Парсинг запроса
1. Вызывается функция `to_normal_case`, приводящая все слова запроса к одному виду для регистронезависимого поиска
2. С помощью функции `remove_additional_words`, создается список без дополнительных слов, которые содержатся
в `street_kinds.txt`.
3. Поиск здания в запросе. Должно начинаться с цифры и идти в конце.
4. Поиск города в запросе.
   1. Последовательно выполняются запросы в базу данных городов, пока город не будет найден.
   2. Выбирается наиболее предположительный вариант с помощью словаря, хранящем в значениях количество совпадений, и 
   вычислением разницы между запросом и всеми вариантами.
   3. Слова, содержащиеся в городу, удаляются из запроса.
5. Поиск улицы происходит аналогично поиску города.
6. Делается запрос в основную базу данных.