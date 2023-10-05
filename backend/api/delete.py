from collections import OrderedDict
d = OrderedDict([('id', 1), ('amount', 10)])


#d = OrderedDict([('Италия', 14), ('Аргентина', 6), ('Бразилия', 2), ('Чехия', 1)])
print(d)
#print((d.items()))
print(list(d.items()))
print(list(d.items())[0][1])
print(list(d.items())[1][0])
# Вывод: [('Италия', 14), ('Аргентина', 6), ('Бразилия', 2), ('Чехия', 1)]