import webcolors

a = 'blue'
#a = '#0000ff'

if a[0] == '#':
    name = a

name = webcolors.name_to_hex('blue')


# print(hex)
print(name)

'''
class Name2HexColor(serializers.Field):
        
    def to_internal_value(self, data):
        
        try:
            data = webcolors.name_to_hex(data)
        except ValueError:
            raise serializers.ValidationError(
                f'Введите вместо {data} название цвета из палитры Basic Colors')
        return data'''