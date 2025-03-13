from django.contrib import admin
from .models import Producto, Pedido, ItemPedido, ClienteAnonimo

admin.site.register(Producto)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(ClienteAnonimo)
