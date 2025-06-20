# Описание
Консольная мини-игра про космос, написанная на `asyncio`. Представляет из себя небольшую аркаду, в которой реализовано звездное небо, космический корабль и падающий звездный мусор. Игра начинается в 1957 году, когда звездолет впервые взлетает в космос, тогда небо чистое и ничего не мешает ему в полете, но в 1961 году корабль впервые встречает на своем пути звездный мусор, который является для него разрушительным препятствием. С каждым годом мусора в космосе становится все больше, а уворачиваться звездолету от него все сложнее и сложнее. В 2020 году мусора стало настолько много, что пришлось вооружить корабль пушкой, чтобы отстреливаться от мусора.

Начните увлекательное путешествие звездолета в космосе и посмотрите, насколько долго вы сможете сохранить корабль в целостности. Отсчет лет представлен в нижнем левом углу. При столкновении звездолета с мусором игра заканчивается, и появляется заставка GameOver.

## Геймплей
Перемещение корабля по звездному небу - стрелочки вверх, вниз, вправо, влево. Стрельба из пушки - пробел.

# Запуск проекта

## Python-version
`3.13.3`

## Установка зависимостей
В проекте используется пакетный менеджер `uv`, для того чтобы установить его, введите следующую команду в терминале:
### для Windows

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
### для macOS и Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
### Установите python v.3.13.3

```bash
uv python install 3.13.3
```

### Запустите скрипт

```bash
uv run main.py
```
# Модули и пакеты

## main.py
Реализация асинхронных анимаций. Каждая функция отвечает за отображение какого-либо кадра на звездном небе.

## curses_tools.py
Функция `draw_frame` - выводит на экран многострочный текст — кадр анимации
Функция `read_controls` - задает направление перемещения корабля и выстрел
Функция `get_frame_size` - вычисляет размер многострочного текста

## explosion.py 
Анимация взрыва.

## game_scenario.py
Реализация сценария игры.

Темп игры и все события привязаны к годам. Один год — это 1.5 секунды игрового времени. Начинаем с 1957 года — года запуска первого искусственного спутника Земли.

До 1961 года в космосе чисто и пусто, затем появляется мусор. Со временем его становится все больше и к 2020 году корабль вооружается плазменной пушкой, чтобы было чем расчищать дорогу.

Чем ближе к 2020 году, тем больше мусора на орбите. Частотой его появления управляет функция `get_garbage_delay_tics`.

Чтобы было совсем антаружно, на экране могут появляться надписи — чем примечателен этот год. За основу можно взять `PHRASES`.

## obstacles.py
Модуль для работы с препятствиями. Помогает вести учет препятствия и отображать на карте место их расположения.

## physics.py
Плавное управление скоростью космического корабля. Учитывает текущую скорость, позволяя кораблю ускоряться и тормозить.

## state.py
Глобальные переменные.

## Каталог frames
Хранится многострочный текст в текстовых файлах - кадры анимаций.

# Результаты
![](https://github.com/zakhar-terekhov/Images/blob/main/space.gif)
